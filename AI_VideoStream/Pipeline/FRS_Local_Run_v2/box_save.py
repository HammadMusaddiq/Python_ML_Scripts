from kafka import KafkaConsumer,KafkaProducer,TopicPartition
import json
import uuid
from ftp_download import Ftp_Save
import json
from kafka import KafkaConsumer,KafkaProducer,TopicPartition
import cv2
from PIL import Image
from datetime import datetime
from multiprocessing import Process
import numpy as np
import multiprocessing
from boxPlot import Plot
from aiRequests import aiRequests
import io
from PIL import Image
import numpy as np
import uuid
from threading import Thread

ftp_save=Ftp_Save()
KAFKA_PORT = "10.100.150.100:9092"
face_topic='captured-faces'
# face_topic_test='captured-faces_test'
# car_topic_test='car_test'
car_topic='captured-cars'
people_topic='captured-pedestrian'

req=aiRequests()




def json_serializer(data):
    return json.dumps(data.copy()).encode()

def send_data(data,topic):
    producer = KafkaProducer(bootstrap_servers=[KAFKA_PORT], 
    value_serializer=json_serializer)
    producer.send(topic, data)

def add_margin(image, x, y, w, h):
    margin=0.03
    img_h, img_w = image.shape[1], image.shape[0]
    xi1 = max(int(x - (margin * w)), 0)
    xi2 = min(int(w + (margin * w)), img_w - 1)
    yi1 = max(int(y - (margin * h)), 0)
    yi2 = min(int(h + (margin * h)), img_h - 1)   
    return xi1, yi1, xi2, yi2

def facesI(recognized_boxes,img,time,camera_ip):
    for face_count,pic in enumerate(recognized_boxes):
        x1, y1, width, height = pic # [1,2,3,5]

        # bug fix
        x1, y1 = abs(x1), abs(y1)
        x2, y2 = x1 + width, y1 + height
        # extract the face

        face_image_api = img[y1:y2, x1:x2] # img: actual image, face: image of face

        pic_new = [pic[0],pic[1],pic[2]+pic[0],pic[3]+pic[1]]
        
        x12,y12,w12,h12 = add_margin(img,pic_new[0],pic_new[1],pic_new[2],pic_new[3])

        try: 
            face_image_display = img[y12:h12, x12:w12] # img: actual image, face: image of face
            # face = cv2.cvtColor(face, COLOR_RGB2BGR)

            facee=dict()
            file_name=str(uuid.uuid4())+'.jpg'
            image_link = ftp_save.imageToFTP("/AIN/Frames/captured_faces", file_name, face_image_api,face_count)
            facee['face_image_api'] = image_link

            # file_name=str(uuid.uuid4())+'.jpg'
            try:
                image_link = ftp_save.imageToFTP("/AIN/Frames/display_faces", file_name, face_image_display,face_count) 
            except: 
                face_image_display = img[y12:h12, x12:x2]
                face_image_display = cv2.resize(face_image_display, (80, 80), interpolation = cv2.INTER_AREA)
                image_link = ftp_save.imageToFTP("/AIN/Frames/display_faces", file_name, face_image_display,face_count) 
                # import pdb; pdb.set_trace()

            facee['face_image_display']=image_link
            facee['c_time']=time
            facee['camera_ip']=camera_ip
            send_data(facee,face_topic)

        except Exception as E:
            print(E)
            print(x1,x2,y1,y2)
 

def frame_ai(img,message,ai_data,action,camera_ip):
    # import pdb;pdb.set_trace()
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    numpy_image = np.uint8(img)
    image = cv2.imencode('.jpg', numpy_image)[1].tobytes() # numpy to bytes
    files={'image_path': image}

    try:
        time1=datetime.now()

        # proc=Process(target=req.smoke_detection,args=(files,return_dict,))
        # proc.start()
        # proc1=Process(target=req.weapon_detection,args=(files,return_dict,))
        # proc1.start()
        if action=='FRS':
            proc2=Process(target=req.frs_detection,args=(files,return_dict,))       
            proc2.start()

        # # proc.join()
        # # proc1.join()
            proc2.join()

        # ai_data['frs_data'] = face_app.search_embeddings(image)

        # time2=datetime.now()
        # print(time2-time1)

        elif action=='ANPR':
            time1=datetime.now()
            proc1=Process(target=req.ANPR,args=(files,return_dict,))       
            proc1.start()
            # proc2=Process(target=req.ANPR_P,args=(files,return_dict,))       
            # proc2.start()
            proc1.join()
            
            time2=datetime.now()

            print(time2-time1)

            # proc2.join()        
        else:
            print('No action Given')
            return

        ai_data=return_dict 
        
        ai_data['kafka_id']=message['kafka_id']
        ai_data['time']=message['time']
        # ai_data['camera_ip']=message['camera_ip']
        ai_data['camera_ip']=camera_ip


        

    except Exception as e:
        import traceback
        print(traceback.print_exc())
        print('Exception in request  ::  ',e)

    if action=='FRS':
        try:
            # print(ai_data)
            recognized_boxes=ai_data['frs_data']['detected_faces']
            time1=datetime.now()
            facesI(recognized_boxes,numpy_image,ai_data['time'],camera_ip)
            time2=datetime.now()
            print(time2-time1)

            # t1=Thread(target=facesI,args=(recognized_boxes,numpy_image,))
            # t1.start()
        except Exception as E:
            print('Problemssss' + str(E))            

    if action=='ANPR':
        try:
            # print(ai_data)
            cars_data=ai_data['ANPR_data']['data'][0]

            # cars_data=ai_data['ANPR_data']['vehicle_data']['car_image_links']
            if len(cars_data)>0:
                send_data(ai_data,car_topic)

        except Exception as E:
            print('Problemssss' + str(E))   
        # try:
        #     people_count=ai_data['People_data']['peopleCount']
        #     if people_count>0:
        #         send_data(ai_data['People_data'],people_topic)

        # except Exception as E:
        #     print('Problemssss' + str(E))                        