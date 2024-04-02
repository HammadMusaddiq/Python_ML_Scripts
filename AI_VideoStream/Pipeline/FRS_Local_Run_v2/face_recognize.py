import json
from kafka import KafkaConsumer,KafkaProducer
import json
import base64
import pickle
import requests
from threading import Thread
from aiRequests import aiRequests








if __name__=='__main__':
    KAFKA_PORT = "10.100.150.100:9092"
    face_topic='captured-faces'
    req=aiRequests()

    consumer=KafkaConsumer(face_topic,bootstrap_servers=[KAFKA_PORT],auto_offset_reset='latest',
    group_id = 'my-group-001')

    for index,message in enumerate(consumer):
        print(index)
        # import pdb;pdb.set_trace()
        message=json.loads(message.value)
        # print(message.keys())
        face=message.get('face_image_api','')
        display_face=message.get('face_image_display','')
        time=message.get('c_time','')
        # imdata = base64.b64decode(face)
        # im = pickle.loads(imdata)
        if face!=False or face!='':
            files={'image_path': face}
            try:
                # req.recognize_face(files,display_face,time)

                t1=Thread(target=req.recognize_face,args=(files,display_face,time))
                t1.start()
            except Exception as E:
                print('MS Down:: ',E)