from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.functions import monotonically_increasing_id
from pyspark.sql.types import *
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import uuid
import time
import configparser
import io
import json
import ast


class OwlsenseStream:
    def __init__(self, read_topic=None, write_topic=None, feature_name=None, concurrent_jobs=10, initalize_config=None):
        """
          read_topic: kafka topic to read from
          write_topic: kafka topic to write to
          group_id: kafka consumer group_id
          feature_name: name of the feature
        """
        if not (read_topic and feature_name):
            raise Exception("read_topic, write_topic, feature_name cannot be NULL")

        # development kafka -> ','.join(['192.168.18.145:9092','192.168.18.146:9092','192.168.18.147:9092'])
        # ambari-kafka -> :6667
        #
        self.kafka_brokers = broker_list
        self.read_topic = read_topic
        self.write_topic = write_topic
        self.start_time = 0
        self.end_time = 0
        self.feature_name = feature_name
        self.stream_hashmap = stream_hashmap

        if initialize_config:
            initialize_config(spark)

    def get_kafka_broker(self):
        return broker_list

    def get_spark_context(self):
        return spark

    def setReadTopics(self, topics=None):
        if topics is None:
            raise Exception("please define atleast one kafka topic")
        self.read_topic = topics

    def readStream(self):
        """
          Reads data from kafka
        """
        kafka_params = {
            "group.id": self.feature_name,
            "auto.offset.reset": "largest",
            "metadata.broker.list": self.kafka_brokers
        }
        if isinstance(self.read_topic, str):
            return KafkaUtils.createDirectStream(ssc, [self.read_topic], kafka_params,
                                                 messageHandler=lambda x: (x.topic, x.message))
        elif isinstance(self.read_topic, list) or isinstance(self.read_topic, tuple):
            return KafkaUtils.createDirectStream(ssc, self.read_topic, kafka_params,
                                                 messageHandler=lambda x: (x.topic, x.message))

    def process(self, rdd, callback):
        """
          rdd: input rdd
          callback: a function to apply operations on dataframe
        """
        if not rdd.isEmpty():
            data = ""
            for row in rdd.collect():
                topic = str(row[0])
                try:
                    data = json.loads(row[1])
                except ValueError:
                    try:
                        data = ast.literal_eval(str(row[1]))
                    except:
                        print("Data Provided in Wrong/Unexpected/non-dict Format, failed to parsed")
                        print(str(row[1]))
                        return None

                data['topic'] = stream_hashmap.get(topic, None)
                if data['topic'] is None:
                    data['topic'] = self.write_topic
                if self.feature_name == 'READ_STREAM':
                    data['data_type'] = topic.replace('-', '_').strip()

                print(json.dumps(data, indent=4))
                data = json.dumps(data)
                df = None
                try:
                    df = spark.read.option('inferSchema', 'true').json(spark.sparkContext.parallelize([data]),
                                                                       multiLine=True)
                except:
                    print("ERROR WHILE READING DATA")
                    print(data)
                    return None

                try:
                    df = callback(df)
                except Exception as E:
                    import traceback
                    traceback.print_exc()
                    self.write_topic = "failed_taks"

                self.writeStream(df)

    def start(self, callback):
        """
          A function to start streaming -> processing -> save
        """
        # def correct_messages(rdd):
        #   for row in rdd.collect():

        # lambda rdd: self.process(rdd,callback)
        output = self.readStream().foreachRDD(lambda rdd: self.process(rdd, callback))
        ssc.start()  # Start the computation
        ssc.awaitTermination()  # Wait for the computation to terminate

    def stop(self):
        ssc.stop()

    def writeStream(self, df=None):
        """
          data: should be a spark dataframe
        """
        if df is None:
            raise Exception("data field cannot be empty should be a spark dataframe")

        df = df.select('topic', to_json(struct([df[x] for x in df.columns])).alias("value"))
        df.selectExpr("CAST(value as STRING)", "topic") \
            .write \
            .format("kafka") \
            .option("kafka.bootstrap.servers", self.kafka_brokers) \
            .save()


def initialize_config(spark):
    global broker_list
    global broker_username
    global broker_password

    parse_str = configparser.ConfigParser()
    c = spark.sparkContext.textFile(conf_path).collect()
    buf = io.StringIO("\n".join(c))
    x = parse_str.readfp(buf)
    broker_list = str(parse_str.get('KAFKA_BROKERS', 'brokers')).strip()
    broker_username = str(parse_str.get('KAFKA_BROKERS', 'username'))
    broker_password = str(parse_str.get('KAFKA_BROKERS', 'password'))


stream_hashmap = {
    "linkedin-user-profile-information": "save",
    "linkedin-user-posts": "data",
    "linkedin-company-profile-information": "save",
    "linkedin-company-posts": "data",
    "instagram-profile-information": "save",
    "instagram-posts": "data",
    "instagram-following": "save",
    "instagram-followers": "save",
    "twitter-posts": "data",
    "twitter-profile-information": "save",
    "twitter-following": "save",
    "twitter-followers": "save",
}

spark = SparkSession.builder \
    .config("spark.streaming.concurrentJobs", str(len(stream_hashmap.keys()))) \
    .config("spark.streaming.backpressure.enabled", "true") \
    .config("spark.locality.wait", "100") \
    .config("spark.streaming.kafka.consumer.poll.ms", 512) \
    .config("spark.streaming.kafka.maxRatePerPartition", '100') \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

ip = "10.100.102.102"
conf_path = "hdfs://{}/user/config/config.ini".format(ip)
broker_list = None
broker_username = None
broker_password = None

# if isinstance(self.read_topic,str):
#   return KafkaUtils.createStream(ssc,self.kafka_brokers,"merge",{self.read_topic:2})
# elif isinstance(self.read_topic,list) or isinstance(self.read_topic,tuple):
#   return KafkaUtils.createStream(ssc,self.kafka_brokers,"merge",{ topic:2 for topic in self.read_topic.split(',')})


initialize_config(spark)

ssc = StreamingContext(spark.sparkContext, 10)

# ssc.checkpoint("/tmp/_checkpoint")


"""
 Example Usage"

def callback(df):
    df = df.select('*')
    return df

stream = OwlsenseStream(read_topic='RAW_DATA',write_topic='DDDD',feature_name="TEST")
stream.start(callback=callback)

"""