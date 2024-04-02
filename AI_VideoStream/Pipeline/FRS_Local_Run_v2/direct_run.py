import json
from cv2 import COLOR_RGB2BGR
from kafka import KafkaConsumer,KafkaProducer,TopicPartition
import cv2
from PIL import Image
from datetime import datetime
from multiprocessing import Process,Value,Lock
import numpy as np
import multiprocessing
from boxPlot import Plot
from aiRequests import aiRequests
import requests
import io
from PIL import Image
import numpy as np
import uuid
from threading import Thread
from box_save import frame_ai


print('Waiting for messages')
KAFKA_PORT = "10.100.150.100:9092"



def video_stream(message):
    # import pdb;pdb.set_trace()
    ############################# Initializing ###########################
    # camera_ip = '192.168.23.199'
    try:
        camera_ip=message.get('camera_ip','')
    except Exception as e:
        print('No Camera  IP given :: ',e)
        return

    # camera_user = 'admin'
    camera_user = message.get('username','')

    # camera_pass ='Admin12345'
    camera_pass =message.get('password','')


    operation=message.get('operations','')
    live_feed = "rtsp://"+camera_user+":"+camera_pass+"@"+camera_ip  # CCTV Camera
    vid = cv2.VideoCapture(live_feed, cv2.CAP_FFMPEG)
    count=0
    ai_data=dict()  
    start=datetime.now()
    frame_count=0
    if operation=='ANPR':
        modulus=30
    elif operation=='FRS':
        modulus=25

    while vid.isOpened():   
        ret, frame = vid.read()
        current_time = datetime.now()
        c_time = current_time.strftime("%d/%m/%Y %I:%M %p")
        count+=1
        # if frame is read correctly ret is True
        if not ret:
            pass
                
        else:
            if count%modulus==0:
                kafka_id=str(uuid.uuid4())
                if operation=='ANPR':
                    cvt_frame=frame
                elif operation=='FRS':
                    cvt_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                frame_detail = {
                    "camera_ip":camera_ip,
                    "kafka_id":kafka_id,
                    "time":c_time,
                    }
                frame_ai(cvt_frame,frame_detail,ai_data,operation,camera_ip)
                frame_count+=1
                print(frame_count,'  ON CAMERA :: ',camera_ip)

    vid.release()


if __name__ == '__main__':
    topic_name='save-camera'
    camera_list=[]
    consumer1 = KafkaConsumer(topic_name,auto_offset_reset='latest',
                            bootstrap_servers=[KAFKA_PORT])
    processes=dict()
    for msg in consumer1:
        message=json.loads(msg.value)
        # import pdb;pdb.set_trace()
        camera_name=message['camera_name']
        camera_action=message['action']

        if camera_name not in camera_list:
            camera_list.append(camera_name)
            print('NO OF ACTIVE CAMERAS ::  ',str(len(camera_list)))



        if camera_action=='Start':
            # video_stream(message)
            processes[camera_name]=Process(target=video_stream,args=(message,))
            processes[camera_name].start()
            print(f"Staring Process for CAMERA {camera_name} with PID: {processes[camera_name].pid}")

        elif camera_action=='Stop':
            try:
                processes[camera_name].terminate()
                camera_list.remove(camera_name)
            except:
                if camera_name not in camera_list:
                    camera_list.append(camera_name)

            print('NO OF ACTIVE CAMERAS ::  ',str(len(camera_list)))




        elif camera_action=='Change':
            try:
                processes[camera_name].terminate()
                camera_list.remove(camera_name)
            except:
                print('NO OF ACTIVE CAMERAS ::  ',str(len(camera_list)))
            # video_stream(message)
            processes[camera_name]=Process(target=video_stream,args=(message,))
            processes[camera_name].start()
            print(f"Staring Process for CAMERA {camera_name} with PID: {processes[camera_name].pid}")            
