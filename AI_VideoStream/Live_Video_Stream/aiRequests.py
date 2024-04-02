# from importlib.metadata import files
import requests
# import cv2
# import io
from PIL import Image
# import numpy as np

class aiRequests():
    '''Class with all the functions for different ai Operations'''

    def smoke_detection(self,files,return_dict):

        # res=requests.post('http://10.100.103.201:6001/insert',data=img.tobytes(),timeout=30)
        res=requests.post('http://0.0.0.0:6001/insert',files=files,timeout=30)

        # print(res.status_code)
        if res.status_code==200:
            # data=res.json()
            return_dict['smoke_data'] = res.json()
        else:
            # data='MS not Working'
            return_dict['smoke_data'] = 'MS not Working'
        # return data

    def weapon_detection(self,files,return_dict):

        res=requests.post('http://0.0.0.0:6002/insert',files=files,timeout=30)
        # res=requests.post('http://10.100.103.200:5017/insert',files=files,timeout=30)

        # print(res.status_code)
        if res.status_code==200:
            # data=res.json()
            return_dict['weapons_data'] = res.json()
        else:
            # data='MS not Working'
            return_dict['weapons_data'] = 'MS not Working'
        # return data    

    def frs_detection(self,files,return_dict):
        

        res=requests.post('http://0.0.0.0:6003/search',files=files,timeout=30)
        # res=requests.post('http://192.168.18.229:5000/search',data=img.tobytes(),timeout=30)

        # print(res.status_code)
        if res.status_code==200:
            # data=res.json()
            return_dict['frs_data'] = res.json()
        else:
            # data='MS not Working'
            return_dict['frs_data'] = 'MS not Working'
        # return data   