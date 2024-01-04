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

app = Flask('FRS-Recognition')
frs_app = FRS_App()


@app.route("/",methods=['GET'])
def hello():
    return "Face Detection model is Up and Running!" , 200
    

def cvtFormatBox(rec_box):
    recog_box = []
    for bx in rec_box:
        recog_box.append([int(val) for val in bx])

    return recog_box

def callingFRS(image):
    embeddings, recognized_boxes = frs_app.frsProcessing(image)
    recognized_boxes  = cvtFormatBox(recognized_boxes)
    matched_results = frs_app.dataExtracting(embeddings)
    return matched_results, recognized_boxes


@app.route("/search",methods=['POST'])
def search_embeddings():
    if request.method == "POST":
        logger.info("Face Detection Started!")
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
            logger.info("Face Detection Frame Searching Started!")
            matched_results, recognized_boxes = callingFRS(image)

            frs_output = {"matched_results" : matched_results,
                "recognized_boxes" : recognized_boxes
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