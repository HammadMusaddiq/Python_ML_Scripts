import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, udf,array
import configparser
import io
import uuid


print("WAITING FOR DATA IN PRE-PROCESSING COMPLETED TOPIC")

# Name of topics to subscribe to using spark structured streaming
topics = "captured-faces"
# Topic to write processed output to
write_topic = "matched-faces"
checkpoint_path = "/home/ubuntu/Desktop/checkp/read_check"


spark = SparkSession \
    .builder \
    .appName("readstream") \
    .getOrCreate()

KAFKA_CONSUMER_IP_PORT = "10.100.150.100:9092"

print("KAFKA BROKER: ", KAFKA_CONSUMER_IP_PORT)


# Function to add Kafka_id and Data_type to the dataframe
def add_kafka(dfo):
    df = dfo[0]
    topic = dfo[1]
    df = json.loads(df)
    df['kafka_id'] = str(uuid.uuid4())
    df['data_type'] = topic.replace("-", "_").strip()
    df['valid'] = 'True'
    return json.dumps(df)


# Reading the data from the topics mentioned above
dsraw = spark \
  .readStream \
  .format("kafka")\
  .option("kafka.bootstrap.servers", KAFKA_CONSUMER_IP_PORT) \
  .option("subscribe", topics) \
  .load()

# creating an udf from the add_kafka function
# lambda_udf = udf(lambda x: add_kafka(x))

# calling udf on the streaming dataframe
# dt = dsraw.withColumn("value", col('value').cast('string')).withColumn("value", lambda_udf(array('value', 'topic')))

# Printing the processed dataframe on the console to verify the output
ds = dsraw.selectExpr("CAST(value AS STRING)") \
    .writeStream \
    .format('console') \
    .option('truncate', False) \
    .option('numRows', 100000) \
    .start()

# Dumping the value from the processed dataframe into Kafka Topics
# dsf = dt.selectExpr("CAST (value AS STRING)") \
#   .writeStream \
#   .format("kafka")\
#   .option("kafka.bootstrap.servers", KAFKA_CONSUMER_IP_PORT) \
#   .option("topic", write_topic) \
#   .option("checkpointLocation", checkpoint_path) \
#   .start()


spark.streams.awaitAnyTermination()
