from importlib.metadata import files
import requests
import cv2
import io
from PIL import Image
import numpy as np
import json
from kafka import KafkaProducer

def json_serializer(data):
    return json.dumps(data).encode()

KAFKA_PORT = "10.100.150.100:9092"
match_face_topic='matched-faces'

def send_match_faces(data):
    producer = KafkaProducer(bootstrap_servers=[KAFKA_PORT], 
    value_serializer=json_serializer)
    producer.send(match_face_topic, data)


class aiRequests():
    '''Class with all the functions for different ai Operations'''

    def smoke_detection(self,files,return_dict):

        # res=requests.post('http://10.100.103.201:6001/insert',data=img.tobytes(),timeout=10)
        res=requests.post('http://0.0.0.0:6001/insert',files=files,timeout=10)

        # print(res.status_code)
        if res.status_code==200:
            # data=res.json()
            return_dict['smoke_data'] = res.json()
        else:
            # data='MS not Working'
            return_dict['smoke_data'] = 'MS not Working'
        # return data

    def weapon_detection(self,files,return_dict):

        res=requests.post('http://0.0.0.0:6002/insert',files=files,timeout=10)
        # res=requests.post('http://10.100.103.200:5017/insert',files=files,timeout=10)

        # print(res.status_code)
        if res.status_code==200:
            # data=res.json()
            return_dict['weapons_data'] = res.json()
        else:
            # data='MS not Working'
            return_dict['weapons_data'] = 'MS not Working'
        # return data    

    def frs_detection(self,files,return_dict):
        

        # res=requests.post('http://0.0.0.0:6005/search',files=files,timeout=10)
        res=requests.post('http://10.100.150.103:6005/search',files=files,timeout=10)
        # res=requests.post('http://192.168.18.229:5000/search',data=img.tobytes(),timeout=10)

        # print(res.status_code)
        if res.status_code==200:
            # data=res.json()
            return_dict['frs_data'] = res.json()
        else:
            # data='MS not Working'
            return_dict['frs_data'] = 'MS not Working'
        # return data   
        
    def ANPR(self,files,return_dict):
            # res=requests.post('http://10.100.103.201:6001/insert',data=img.tobytes(),timeout=30)
            res=requests.post('http://10.100.150.103:6002/vehicle',files=files,timeout=30)
            if res.status_code==200:
                # data=res.json()
                ANPR_data=res.json()
                return_dict['ANPR_data'] = ANPR_data
            else:
                # data='MS not Working'
                return_dict = 'MS not Working'
            # return data    
            # 
    def ANPR_P(self,files,return_dict):
            res=requests.post('http://10.100.150.103:6002/people',files=files,timeout=30)
            if res.status_code==200:
                # data=res.json()
                People_data=res.json()
                return_dict['People_data'] = People_data
            else:
                # data='MS not Working'
                return_dict = 'MS not Working'
            # return data                   

    def recognize_face(self,files,display_face,time):
        data=dict()
        # res=requests.post('http://10.100.150.103:6006/search',files=files,timeout=10)
        res=requests.post('http://10.100.150.103:6006/search',data=files,timeout=10)
        
        data['orignal_face']=files.get('image_path')
        data['display_face']=display_face
        data['c_time']=time



        if res.status_code==200:
            rec_data=res.json()
            # matched_person = rec_data['matched_results']['detected_person']
            matched_person = rec_data['matched_results']


            res = [ele for ele in matched_person if ele != []] ######### Fore deleting empty lists from list
            # print(matched_person)
            if len(res)>0 and type(res[0]) == dict and res[0]!='':
                # import pdb;pdb.set_trace()
                # distance=rec_data['matched_results']["matched_images"][0].get('distance')
                distance=res[0].get('distance')
                id=res[0].get('id')


                # perc=100-((abs(45-distance)/30)*100) #percentage on 65% threshold
                percentage = 100/(100+(distance-30))*100
                if percentage >= 100:
                    percentage = 99

                data['match_data']=dict()
                data['match_data']['percentage']=percentage
                data['match_data']['id']=id
                # data['match_data']=rec_data
                send_match_faces(data)
            # print(data)
        else:
            data['match_data']='Error in MS'