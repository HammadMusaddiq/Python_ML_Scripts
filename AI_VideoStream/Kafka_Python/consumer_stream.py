from kafka import KafkaConsumer
# from pymongo import MongoClient
from json import loads
import json
import cv2
import numpy as np
import base64
import pickle
import requests
import io
from PIL import Image

topic = "ai-live-feed"
# import pdb;pdb.set_trace()
consumer = KafkaConsumer(
     topic,
     bootstrap_servers=['10.100.103.125:9092'],
     group_id=None,
    ) 
    # 'latest', auto_offset_reset='earliest',


for message in consumer:
    data = json.loads(message.value)
    
    
    imdata = base64.b64decode(data['image'])
    print(type(imdata))
    im = pickle.loads(imdata)
    print(im.shape)

    import pdb;pdb.set_trace()
    # files={'image': open(io.BytesIO(im), 'rb')}


    node_ip = 'localhost'
    node_port = '5000'
    path = 'search'

    image = cv2.imencode('.jpg', im)[1].tobytes()
    print(type(image))

    # image = Image.fromarray(np.uint8(im))
    # # image = image.convert("RGBA")
    # # image = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    # temp = io.BytesIO() # This is a file object
    # image.save(temp, format="png") # Save the content to temp
    # temp.seek(0) 

    files={'image': image}
    
    response = requests.post(f"http://{node_ip}:{node_port}/{path}",files=files)
    print(response)
    data = response.json()
    print(data)


