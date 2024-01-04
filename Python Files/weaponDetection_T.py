import configparser

import requests
from elasticsearch import Elasticsearch
import pyspark.sql.functions as F
from pyspark.sql import SparkSession
import io
import json


def get_entities(list_of_pictures):
    for pic in list_of_pictures:
        res = requests.post('http://{}:{}/'.format())
        result.append(res[])


def callback(x):
    x = x.decode('utf-8')
    es = Elasticsearch(f"http://{esip}:{esport}")
    x = json.loads(x)

    if 'media_c' not in x.keys():
        print("=======================================medic_c not found in the data~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(x.get('kafka_id'))
        return json.dumps(x)

    # x['weapon_detection'] = get_entities(x['media_c'])


topic_name = 'preprocessing_completed'
write_topic = "weapon_detection_processed"
ip = ''
conf_path = "hdfs://{}/user/config/config.ini".format(ip)  # Config Path
checkpoint_location = "/home/ubuntu/Desktop/checkp/weapon_checkp"
print("Configuration File Path: ", conf_path)

spark = SparkSession \
    .builder \
    .appName("SSKafka") \
    .getOrCreate()
# ============================= Reading Config =============================
credstr = spark.sparkContext.textFile(conf_path).collect()
buf = io.StringIO("\n".join(credstr))

parser = configparser.ConfigParser()
parser.read_file(buf)
node_ip_ftp = str(parser.get('FTP', 'host')).strip()
node_port_ftp = str(parser.get('FTP', 'port')).strip()
auth_user_ftp = str(parser.get('FTP', 'username')).strip()
auth_pass_ftp = str(parser.get('FTP', 'password')).strip()

node_ip_objd = str(parser.get('OBJD_FLASK', 'ip')).strip()
node_port_objd = str(parser.get('OBJD_FLASK', 'port')).strip()
esip = str(parser.get('BDS_ES_PROD', 'ip'))
esport = str(parser.get('BDS_ES_PROD', 'port'))

KAFKA_CONSUMER_IP = str(parser.get('KAFKA_BROKERS', 'brokers'))
# ============================= END =============================

# Reading data from the Kafka Topic

dfraw = spark.readStream.format('kafka') \
    .option('kafka.bootstrap.servers', KAFKA_CONSUMER_IP) \
    .option('subscribe', topic_name) \
    .load()

calludf = F.udf(lambda x: callback(x))

df = dfraw.withColumn('value', calludf(dfraw['value'])) \
    .select('value')

ds = df.selectExpr("CAST(value AS STRING)") \
    .writeStream \
    .format('console') \
    .option('truncate', False) \
    .option('numRows', 100000) \
    .start()

dsf = df.selectExpr("CAST (value AS STRING)") \
    .writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_CONSUMER_IP) \
    .option("topic", write_topic) \
    .option("checkpointLocation", checkpoint_location) \
    .start()


spark.streams.awaitAnyTermination()
