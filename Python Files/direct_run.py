import json
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
from ftp_download import Ftp_Save
import uuid




def json_serializer(data):
    return json.dumps(data).encode()


def send_data(data):
    producer = KafkaProducer(bootstrap_servers=[KAFKA_PORT], 
    value_serializer=json_serializer)
    producer.send(ai_topic, data)

def notify_send_data(data):
    producer = KafkaProducer(bootstrap_servers=[KAFKA_PORT], 
    value_serializer=json_serializer)
    producer.send(notification_topic, data)    
############################# Initializing END ###########################


print('Waiting for messages')




def frame_ai(img,message,frame_count,ai_data,frames_list):

    # video_length_in_sec=30
    manager = multiprocessing.Manager()

    # start_time=datetime.now()



    notify_list=[]

    return_dict = manager.dict()


    # response = requests.get(img)
    # img = Image.open(io.BytesIO(response.content)) 

    numpy_image = np.uint8(img)
    image = cv2.imencode('.jpg', numpy_image)[1].tobytes() # numpy to bytes
    files={'image_path': image}
    ####################### Sending Every 5th frame for AI op #######################

    # if frame_count%5==0:
    # print(index)

    try:
        # time1=datetime.now()
        # proc=Process(target=req.smoke_detection,args=(files,return_dict,))
        # proc.start()
        # proc1=Process(target=req.weapon_detection,args=(files,return_dict,))
        # proc1.start()
        proc2=Process(target=req.frs_detection,args=(files,return_dict,))       
        proc2.start()

        # proc.join()
        # proc1.join()
        proc2.join()

        # time2=datetime.now()
        # print(time2-time1)

        ai_data=return_dict 
        
        ai_data['kafka_id']=message['kafka_id']
        ai_data['time']=message['time']
        # ai_data['frame']=message['image']
        ai_data['camera_ip']=message['camera_ip']
        # import pdb;pdb.set_trace()

        # print(ai_data)
        

    except Exception as e:
        import traceback
        print(traceback.print_exc())
        print('Exception in request  ::  ',e)

    # else:
    #     # import pdb;pdb.set_trace()    

    #     ai_data=ai_data
    #     ai_data['kafka_id']=message['kafka_id']
    #     ai_data['time']=message['time']
    #     # ai_data['frame']=message['image']
    #     ai_data['camera_ip']=message['camera_ip']
    ################ File name for saving  Image ######################
            
    file_name=message['kafka_id']+'.jpg'


    ############ For saving Images ###################
    # Filename
    # filename = '/home/hamza/Downloads/savedImage.jpg'
    # filename1='/home/hamza/Downloads/ai_ops.jpg'




    # Using cv2.imwrite() method
    # Saving the image
    # cv2.imwrite(filename, numpy_image)


    ################# Ploting ####################
    # ann_image=''
    
    try:
        if ai_data['frs_data']!='MS not Working':
            ann_image=plot.frs_plot(ai_data,numpy_image)
            # if str(type(ann_image))=="<class 'numpy.ndarray'>":
                # cv2.imwrite(filename1, ann_image)
                # frames_list.append(ann_image)

        else:
            ann_image=numpy_image


        # if ann_image!='':
        #     ann_image=ann_image
        # else:
        #     ann_image=numpy_image

        # if ai_data['weapons_data']!='MS not Working':
        #     ann_image=plot.weapons_plot(ai_data,ann_image)
        #     # cv2.imwrite(filename1, ann_image)

        #     # import pdb;pdb.set_trace()
        # else:
        #     ann_image=numpy_image 
                
        # if ai_data['smoke_data']!='MS not Working':

        #     ann_image=plot.smoke_det(ai_data,ann_image)
        #     frames_list.append(ann_image)
        #     # cv2.imwrite(filename1, im)
        #     # if return_dict['smoke_data']['Label']=='Fire/Smoke':
        #     #     # import pdb;pdb.set_trace()
        #     #     pass
        # else:
        #     ann_image=numpy_image                
    except Exception as e:
        ann_image=numpy_image
        print(e)

    ####################### For Video Saving #######################
    if len(frames_list)==video_length_in_sec*7:
        # import pdb;pdb.set_trace()    

        plot.createVideo(frames_list,ann_image.shape,7)
        frames_list=[]
        # end_time=datetime.now()
        # print(end_time-start_time)
        # start_time=datetime.now()

    ####################### Video Saving End #######################


    ################### Sending DATA to AI topic ###################
    ######### Notification Image ############
#     try:
#         if ai_data['smoke_data']['Label']== 'Fire/Smoke':
#             if 'Fire/Smoke Detected' not in notify_list:
#                 notify_list.append('Fire/Smoke Detected')
#     except Exception as e:
#         print('Response Not correct From Smoke service  ::  ',e)

#     try:
#         if len(ai_data['weapons_data']['label'])>0:
#             if 'Weapon Detected' not in notify_list:
#                 notify_list.append('Weapon Detected')
#     except Exception as e:
#         print('Response Not correct From Weapons service  ::  ',e)   

#     try:  
#         # import pdb;pdb.set_trace()
#         main_list=ai_data['frs_data']["matched_results"]["detected_person"]
#         res = [ele for ele in main_list if ele != []] ######### Fore deleting empty lists from list
#         ai_data['frs_data']["matched_results"]["detected_person"]=res
#         if len(res)>0:
#             if 'Person Detected' not in notify_list:
#                 notify_list.append('Person Detected')   
#     except Exception as e:
#         print('Response Not correct From FRS service  ::  ',e) 

#     if len(notify_list)>0:
#         image_link = ftp_save.imageToFTP("/AIN/Frames/Notification_Images", file_name, ann_image,frame_count)
#         ai_data['frame']=image_link
#         ai_data['detection']=notify_list
#         notify_send_data(ai_data.copy())

# ############## Saving Image ##########################

#     if (ai_data['weapons_data']=='MS not Working') or (ai_data['smoke_data']=='MS not Working') or (ai_data['smoke_data']=='MS not Working'):
#         ai_data['frame']='Microservice Down'
#     else:
#         image_link = ftp_save.imageToFTP("/AIN/Frames/cv_provessed", file_name, ann_image,frame_count)
#         ai_data['frame']=image_link
#     send_data(ai_data.copy())


#     return ai_data
# ######################################### Notification Sending End #############################################






if __name__ == '__main__':
    ############################# Initializing ###########################
    KAFKA_PORT = "10.100.150.100:9092"
    ai_topic="cv-processed"
    notification_topic='notifications'
    req=aiRequests()
    plot=Plot()
    ftp_save=Ftp_Save()
    lock=Lock()
    main_index=Value('i',0)
    camera_ip = '192.168.23.199'
    camera_user = 'admin'
    camera_pass ='Admin12345'
    video_length_in_sec=60
    live_feed = "rtsp://"+camera_user+":"+camera_pass+"@"+camera_ip  # CCTV Camera
    vid = cv2.VideoCapture(live_feed, cv2.CAP_FFMPEG)
    count=0
    ai_data=dict()  
    frames_list=[]
    start=datetime.now()
    frame_count=0
    while vid.isOpened():   
        ret, frame = vid.read()
        current_time = datetime.now()
        c_time = current_time.strftime("%d/%m/%Y %H:%M:%S")
        count+=1
        # if frame is read correctly ret is True
        if not ret:
            pass
                
        else:
            if count%3==0:
                if frame_count%70==0:
                    print('Frames Done :: ',frame_count)
                    end=datetime.now()
                    print('Time Taken for 70 frames :: ',end-start)  
                    # import pdb;pdb.set_trace()

                    start=datetime.now()

                
                kafka_id=str(uuid.uuid4())
                
                # file_name=kafka_id+'.jpg'
                cvt_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                # image_link = ftp_save.imageToFTP("/AIN/Frames/Images", file_name, cvt_frame,frame_count)
                test = {
                    "camera_ip":camera_ip,
                    "kafka_id":kafka_id,
                    "time":c_time,
                    }
                # send_data(test)     
                ai_data=frame_ai(cvt_frame,test,frame_count,ai_data,frames_list)
                frame_count+=1

                print(frame_count)

    vid.release()