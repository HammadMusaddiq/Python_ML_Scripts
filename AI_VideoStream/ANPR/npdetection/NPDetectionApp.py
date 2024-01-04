# for no tensorflow warnings
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import cv2
import matplotlib.pyplot as plt
from npdetection.local_utils import detect_lp
#from local_utils import detect_lp
from tensorflow.keras.models  import model_from_json
import re
from PIL import Image
import numpy as np
import logging
import logging.handlers
import requests
import json
import time


import pdb

logger = logging.getLogger(__name__)
if (logger.hasHandlers()):
    logger.handlers.clear()

formatter = logging.Formatter('%(asctime)s | %(name)s |  %(levelname)s | %(message)s')
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("app.log")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

logger.info("App started")

class NPDetection:
    def __init__(self):
        self.model_path = "npdetection/models/wpod-net"
        self.model = self.load_model(self.model_path)
        self.api_key = 'K83433112388957'
        self.lang = 'eng'
        self.overlay = 'true'

    # Method to load Keras model weight and structure files
    def load_model(self,path):
        try:
            with open(path+'.json', 'r') as json_file:
                model_json = json_file.read()
            model = model_from_json(model_json, custom_objects={})
            # new_path = 'models/wpod_net_all_in_one'
            model.load_weights(path+'.h5')
            #print("Model Loaded successfully...")
            return model
        except Exception as e:
            logger.error(e)

    def preprocess_image(self, image_url,resize=False):
        
        # response = requests.get(image_url)
        # img = Image.open(BytesIO(response.content))
        # img = np.uint8(img)
        # #img = cv2.imread(image_url) # for reading image from directory
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # pdb.set_trace()
        # print(img)
        img = image_url
        img = img / 255
        
        if resize:
            img = cv2.resize(img, (224,224))
        return img

    def get_plate(self, imageUrl, Dmax=608, Dmin = 608):
        vehicleImg = self.preprocess_image(imageUrl)
        
        ratio = float(max(vehicleImg.shape[:2])) / min(vehicleImg.shape[:2])
        
        side = int(ratio * Dmin)
        bound_dim = min(side, Dmax)
        _ , LpImg, _, cor = detect_lp(self.model, vehicleImg, bound_dim, lp_threshold=0.5)
        return vehicleImg, LpImg, cor

    def img_ocr(self, img_path):        
        ## To read image_path for ocr
        payload = {'isOverlayRequired': self.overlay,
            'apikey': self.api_key,
            'language': self.lang,
            }

        with open(img_path, 'rb') as f:
            r = requests.post('https://api.ocr.space/parse/image',
                files={img_path: f},
                data=payload,
                )

        con = json.loads(r.text)

        return con['ParsedResults'][0]['ParsedText']

    def plate_preproces(self, plate):
        plate = ''.join(e for e in plate if e.isalnum()) # remove special characters
        
        plate = re.sub('(\d+(\.\d+)?)', r' \1 ', plate).strip() # space between text and number
        

        #plate = re.sub(r'([a-z](?=[A-Z])|[A-Z](?=[A-Z][a-z]))', r'\1 ', plate).strip() # space before small and capital letters
    
        # string to list to check words
        splits = plate.split()
        if len(splits) > 3:
            for word in splits:
                if not (re.search('^[0-9]+$', word)) and len(word) > 4: # if word is not number
                    if word[0].isupper() and word[-1].islower(): # word start with upper and end lower case, removed from string
                        plate = plate.replace(word, "").strip()
        
        
        return plate



    def plate_detection(self, imageUrl):
        
        logger.info("Licence number plate detection started!")
        try:
            # get the start time of Number plate dectection
            npst = time.time()
            _, LpImg, _ = self.get_plate(imageUrl) # licence plate image
            logger.info("Licence plate is Found for this vehicle!")
            # get the end time of Number plate dectection
            npet = time.time()
            # get the total execution time of Number plate dectection
            npelapsed_time = npet - npst
            print('----------------------------------- Number plate dectection Execution time for single image:', npelapsed_time, 'seconds')

            logger.info("Reading text...")



            # numpy string to numpy int
            formatted = (LpImg[0] * 255 / np.max(LpImg[0])).astype('uint8')

            formatted = cv2.cvtColor(formatted, cv2.COLOR_BGR2RGB)

            # numpy array to Image
            plate_output = 'plate_read.jpg'
            plate_img = Image.fromarray(formatted)
            plate_img.save(plate_output)

            # read image
            im = cv2.imread(plate_output)
            im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
            
          
            # enhance image
            im1 = cv2.detailEnhance(im, sigma_s=25, sigma_r=0.15)
            plate_img = Image.fromarray(im1)
            plate_img.save('im1.jpg')

            # set threshold on image
            _ , thresh1 = cv2.threshold(im1, 60, 255, cv2.THRESH_BINARY)
            plate_img = Image.fromarray(thresh1)
            plate_img.save('th1.jpg')

            # identify text from image
            # get the start time of OCR
            ost = time.time()
            plate = self.img_ocr('th1.jpg').strip()
            
            # set filter if no text detected
            if plate == '':
                plate = self.img_ocr('im1.jpg').strip()
                

            if plate == '':
                kernel = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
                im2 = cv2.filter2D(src=im1, ddepth=-1, kernel=kernel)

                plate_img = Image.fromarray(im2)
                plate_img.save('im2.jpg')

                _ , thresh2 = cv2.threshold(im2, 80, 255, cv2.THRESH_BINARY)
                plate_img = Image.fromarray(thresh2)
                plate_img.save('th2.jpg')
                
                plate = self.img_ocr('th2.jpg').strip()
                
                        
            if plate == '':
                plate = self.img_ocr('im2.jpg').strip()
                


            if len(plate) >= 3:
                self.plate_preproces(plate)
                

            elif len(plate) < 2: # then read input image directly
                ## To read image_url for ocr
                r = requests.get('https://api.ocr.space/parse/imageurl?apikey='+self.api_key+'&url='+imageUrl+'&language='+self.lang+'&isOverlayRequired='+self.overlay)
                con = json.loads(r.text)
                plate = con['ParsedResults'][0]['ParsedText'].strip()
                

            else: # if len(plate) == 2
                plate = ''
                # print("Number plate is:", plate)


            # get the end time of OCR
            oet = time.time()
            # get the execution time of OCR
            oelapsed_time = oet - ost
            print('----------------------------------- OCR Execution time of signle image:', oelapsed_time, 'seconds')

            logger.info("Number plate is: " + str(plate))
            
            return plate

        except Exception as e:
            
            try:
                r = requests.get('https://api.ocr.space/parse/imageurl?apikey='+self.api_key+'&url='+imageUrl+'&language='+self.lang+'&isOverlayRequired='+self.overlay)
                con = json.loads(r.text)
                plate = con['ParsedResults'][0]['ParsedText'].strip()

                plate = self.plate_preproces(plate)

                return plate

            except:
                logger.error(e)
                # print(e)
                return ''