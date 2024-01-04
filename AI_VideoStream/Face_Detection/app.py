from unittest import result
import cv2
import numpy as np

from flask import Flask
from flask import request

from frs_stream import FRS_Stream

import logging

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

app = Flask('Face-Detection')
model = FRS_Stream()

@app.route("/",methods=['GET'])
def hello():
    return "Face Detection model is Up and Running!" , 200


def frsProcessing(image):
    try:
        face_prediction = model.predict(image)
        detected_boxes = face_prediction['detected_boxes']            
        return detected_boxes

    except Exception as E:
        error = "An Exception Occured: {}".format(E)
        logger.error(error)
        return False


def cvtFormatBox(de_box):
    detect_box = []
    for bx in de_box:
        detect_box.append([int(val) for val in bx])
    return detect_box


def callingFaceSearch(image_array):
    detected_boxes = frsProcessing(image_array)
    detected_boxes  = cvtFormatBox(detected_boxes)
    return detected_boxes


@app.route("/search",methods=['POST'])
def search_embeddings():
    if request.method == "POST":
        logger.info("Face Detection Started!")
        try:
            image = request.files['image_path']
        except:
            try:
                nparr = np.fromstring(request.data, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            except:
                logger.error("Error 400: Bad Input")
                return "Error 400: Bad Input", 400

        try:
            face_boxes = callingFaceSearch(image)

            logger.info("Face Detection Exited!")
            return {"detected_faces" : face_boxes}

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