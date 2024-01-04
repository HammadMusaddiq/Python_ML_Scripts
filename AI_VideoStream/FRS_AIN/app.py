from unittest import result
import cv2
from datetime import datetime
from PIL import Image
import io
import numpy as np
import requests

from flask import Flask
from flask import request

from frs_app import FRS_App
from ftp_stream import Ftp_Stream

import logging
import os
import time

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

app = Flask('AIN-FRS')
ftp_class = Ftp_Stream()
frs_app = FRS_App()
base_url = ftp_class.getBaseURL()
ftp_cursor = ftp_class.getFTP()


@app.route("/",methods=['GET'])
def hello():
    return "AIN-FRS is Up and Running!" , 200

def imageToFTP(path, file_name, image):
    if str(type(image)) != "<class 'numpy.ndarray'>":
        image = transformImage(image)

    image_array = Image.fromarray(np.uint8(image)).convert('RGB')
    image_bytes = io.BytesIO() 
    image_array.save(image_bytes, format="png") 
    image_bytes.seek(0)

    logger.info('Uploading Image to FTP')
    if not ftp_class.is_connected():
        ftp_class.retry_ftp_connection()
        ftp_class.change_ftp_present_working_dir(path)
    else:
        ftp_class.change_ftp_present_working_dir(path)
    
    try:
        baseurl = base_url # ('str' object has no attribute 'copy')
        for p in path.split('/')[1:]:
            baseurl = baseurl + "/" + str(p)
        ftp_file_url = baseurl + "/" + file_name
        ftp_cursor.storbinary("STOR " + file_name , image_bytes)
        # ftp_cursor.quit()
        
        logger.info("Image saved on Ftp URL: "+str(ftp_file_url))
        return ftp_file_url

    except Exception as E:
        logger.error("something went wrong... Reason: {}".format(E))
        return False


def transformImage(image):
    try: # read image_url
        response = requests.get(image)
        img = Image.open(io.BytesIO(response.content))
    except: # read image_bytes
        try:
            img = Image.open(image)
        except:
            img = Image.open(io.BytesIO(image))

    arr = np.uint8(img)

    image_shape = arr.shape
    if image_shape[2] != 3: # convering image to 3 channels for extracting embeddings
        arr = arr[:,:,:3]
    return arr


def plotAnnotation(recognized_boxes, missed_boxes, image_label, image):
    if str(type(image)) != "<class 'numpy.ndarray'>":
        image = transformImage(image)

    # plot annotation
    annotated_image = image
    if isinstance(image_label, str):
        image_label = [image_label]

    for box, label in zip(recognized_boxes,image_label):
        if label == []:
            label = "Unknown"
        annotated_image = cv2.rectangle(annotated_image, (box[0], box[1]), (box[2]+box[0], box[3]+box[1]), (255,0,0), 3) 
        annotated_image = cv2.putText(annotated_image, label, (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,0,0), 2)
    
    for mbox in missed_boxes:
        annotated_image = cv2.rectangle(annotated_image, (mbox[0], mbox[1]), (mbox[2]+mbox[0], mbox[3]+mbox[1]), (255,255,0), 3)
    
    return annotated_image


def filename(p_name):
    ctime = str(datetime.now().timestamp()).replace(".","")
    if p_name:
        f_name = str(ctime) + "_" + p_name + ".jpg"
        return f_name
    else:
        return str(ctime) + ".jpg"


def extractListDiff(detected_boxes, recognized_boxes):
    mainlist = [tuple(x) for x in detected_boxes]
    sublist = [tuple(y) for y in recognized_boxes]
    diff = list(set(mainlist) - set(sublist))
    return diff


@app.route("/insert",methods=['POST'])
def insert_embeddings():
    if request.method == "POST":
        logger.info("AI-Video-Anlaytics Image Inserting Started!")
        
        try:
            image = request.files['image_path']
            person_name = request.form['person_name']
        except:
            try:            
                nparr = np.fromstring(request.data, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            except:
                logger.error("Error 400: Bad Input")
                return "Error 400: Bad Input", 400

        try:
            file_name = filename(person_name)
            embeddings, detected_boxes, recognized_boxes = frs_app.frsProcessing(image)
            # missed_boxes = extractListDiff(detected_boxes, recognized_boxes)
            
            annotated_image = plotAnnotation(recognized_boxes, [], person_name, image)

            image_link = imageToFTP("/AI_Video_Analytics/Image_Upload/Images", file_name, image)     
            annotated_image_link = imageToFTP("/AI_Video_Analytics/Image_Upload/Annotated_Images",file_name, annotated_image)

            stored_id = frs_app.dataStoring(embeddings, recognized_boxes, image_link, annotated_image_link)
            logger.info('Data inserted successfully, Process Ending.')
            return stored_id

        except Exception as E:
            error = "An Exception Occured: {}".format(E)
            logger.error(error)
            return error,500
        

                
    else:
        error = "Error 405: Method Not Allowed"
        logger.error(error)
        return error, 405


def cvtFormatBox(de_box, rec_box):
    detect_box = []
    recog_box = []
    for bx in de_box:
        detect_box.append([int(val) for val in bx])

    for bx in rec_box:
        recog_box.append([int(val) for val in bx])

    return detect_box, recog_box


def callingFRS(image_array):
    embeddings, detected_boxes, recognized_boxes = frs_app.frsProcessing(image_array)
    detected_boxes, recognized_boxes  = cvtFormatBox(detected_boxes, recognized_boxes)
    missed_boxes = extractListDiff(detected_boxes, recognized_boxes)
    matched_results = frs_app.dataExtracting(embeddings)
    return matched_results, recognized_boxes, missed_boxes


@app.route("/search",methods=['POST'])
def search_embeddings():
    if request.method == "POST":
        logger.info("AI-Video-Anlaytics Live Feed Started!")
        try:
            image = request.files['image_path'] # image in bytes Body Form Data (file)
        except:
            try:
                image = request.json['image_path'] # image_url from Body Raw Json
            except:
                try:
                    image = request.form['image_path'] # image_url from Body Form Data (text)
                except:
                    try:
                        nparr = np.fromstring(request.data, np.uint8) # image in bytes from kafka
                        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    except:
                        logger.error("Error 400: Bad Input")
                        return "Error 400: Bad Input", 400

        try:
            logger.info("AI-Video-Anlaytics Frame Searching Started!")
            matched_results, recognized_boxes, missed_boxes = callingFRS(image)

            frs_output = {"matched_results" : matched_results,
                "recognized_boxes" : recognized_boxes,
                "missed_boxes" : missed_boxes
            }
            return frs_output

        except Exception as E:
            error = "An Exception Occured: {}".format(E)
            logger.error(error)
            return error,500
                
    else:
        error = "Error 405: Method Not Allowed"
        logger.error(error)
        return error, 405


if __name__ == "__main__":
    app.run(debug=False)