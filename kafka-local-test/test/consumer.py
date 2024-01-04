from kafka import KafkaConsumer
# from pymongo import MongoClient
from json import loads
import json

topics = ["hammad-test"]
# import pdb;pdb.set_trace()
consumer = KafkaConsumer(
    'notifications',
     bootstrap_servers=['10.100.102.101:6667'],
     auto_offset_reset='earliest',
     group_id=None,
    )
for message in consumer:

    print(json.loads(message.value))

print("quit")