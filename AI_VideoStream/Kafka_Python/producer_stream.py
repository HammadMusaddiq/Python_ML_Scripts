from datetime import datetime
import time
import json
from kafka import KafkaProducer
import cv2
from datetime import datetime
import random
import uuid
import base64
import pickle

def json_serializer(data):
    return json.dumps(data).encode("utf-8")


def send_data(data):
    
    producer = KafkaProducer(bootstrap_servers=['10.100.103.125:9092'], value_serializer=json_serializer)
    producer.send("ai-live-feed", data)


if __name__ == "__main__":

    counter = 0
    frame_counter = 0
    
    vid = cv2.VideoCapture("rtsp://admin:Rapidev@321@192.168.23.158/camera", cv2.CAP_FFMPEG)
    while vid.isOpened():
        ret, frame = vid.read()
        # if frame is read correctly ret is True
        if not ret:
            print("No Frame")
            break
        

        if counter ==5 or counter == 15:
            current_timestamp = str(datetime.now()).replace(' ','_').replace('-','').replace(':','').split('.')[0]
            if counter == 15:
                counter=0
            print("Reading Frame...")  

            # cv2.imwrite("Downloads/img"+str(current_time)+".jpg", frame)

            current_timestamp = str(datetime.now()).replace(' ','_').replace('-','').replace(':','').split('.')[0]
            idx = current_timestamp+'_'+str(frame_counter)
            if frame_counter == 1:
                frame_counter=0
            else:
                frame_counter += 1
            
            imdata = pickle.dumps(frame)
            img = base64.b64encode(imdata).decode('ascii')

            test = {"image":img}
            
            time.sleep(10)
            send_data(test)

            # cv2.imshow('VIDEO', frame)
            # if cv2.waitKey(1) == ord('q'):
            #     break

        counter += 1
    vid.release()                    
    cv2.destroyAllWindows()
  