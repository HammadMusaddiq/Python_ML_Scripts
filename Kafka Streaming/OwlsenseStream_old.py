from pyspark import streaming
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.functions import explode
from pyspark.sql.functions import grouping_id
from pyspark.sql.types import *
import json
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils


class OwlsenseStream:
      def __init__(self,read_topic=None,write_topic=None,feature_name=None,concurrent_jobs=3):
            """
              read_topic: kafka topic to read from
              write_topic: kafka topic to write to
              group_id: kafka consumer group_id
              feature_name: name of the feature 
            """
            if not (read_topic and write_topic and feature_name):
              raise Exception("read_topic, write_topic, feature_name and group_id cannot be NULL")
            
            self.spark = SparkSession.builder\
              .config("spark.streaming.concurrentJobs",str(concurrent_jobs))\
              .appName(feature_name)\
              .getOrCreate()
            self.ssc = StreamingContext(self.spark.sparkContext, 1)
            self.kafka_brokers =  "192.168.18.145:9092,192.168.18.146:9092,192.168.18.147:9092"
            self.read_topic = read_topic
            self.write_topic = write_topic
          
      def readStream(self):
            """
              Reads data from kafka
            """
            return KafkaUtils.createDirectStream(self.ssc,[self.read_topic], {"metadata.broker.list":self.kafka_brokers})
            
      def process(self,rdd,callback):
        """
          rdd: input rdd
          callback: a function to apply operations on dataframe 
        """
        if not rdd.isEmpty():
          # Read RDD as Spark DataFrame
          df = self.spark.read.option('inferSchema','true').json(rdd,multiLine=True)
          # Collection GTR,CTR,Target_Type,Target_Subtype Information
          data = callback(df)
          self.writeStream(data)
        
        
        
      
      def start(self,callback):
            """
              A function to start streaming -> processing -> save 
            """
            output = self.readStream().map(lambda x: str(x[1])).foreachRDD(lambda row: self.process(row,callback))
            self.ssc.start()             # Start the computation
            self.ssc.awaitTermination()  # Wait for the computation to terminate


      def writeStream(self,data=None):
            """
              data: should be a spark dataframe
            """
            if data is None:
                  raise Exception("data field cannot be empty should be a spark dataframe")
                
            data = data.select(to_json(struct([data[x] for x in data.columns])).alias("value"))
            data.selectExpr("CAST(value as STRING)")\
            .write\
            .format("kafka")\
            .option("kafka.bootstrap.servers", self.kafka_brokers)\
            .option("topic",self.write_topic)\
            .save()        
                  


"""
 Example Usage"

def callback(df):
    df = df.select('*')
    return df

stream = OwlsenseStream(read_topic='RAW_DATA',write_topic='DDDD',feature_name="TEST")
stream.start(callback=callback)

"""
