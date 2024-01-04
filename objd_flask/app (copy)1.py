from flask import Flask
from flask import request

import cv2
import json
from skimage import io
import io as ioo
from models.load_models import load_model
import datetime
from ftplib import FTP, error_perm
import numpy as np

import uuid
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog
from detectron2 import model_zoo
from PIL import Image
import matplotlib.pyplot as plt

app = Flask('OBJD')
predictor, cfg = load_model()

#FTP Credentials
HOST = '192.168.18.33'
PORT = 21
USERNAME = 'microcrawler'
PASSWORD = 'rapidev'

BASE_URL = "http://192.168.18.33/osint_system/media_files/Object_Detection/"

ftp = FTP()
def connect(ftp):
    try:
        ftp.connect(HOST, PORT)
        return True
    except error_perm as e:
        print(e)
        return False

def login(ftp):
    try:
        ftp.login(USERNAME, PASSWORD)
        return True
    except error_perm as e:
        print(e)
        return False

def directory_exists(ftp, dir):
    filelist = []
    ftp.retrlines('LIST', filelist.append)
    #print(filelist)
    for f in filelist:
        if f.split()[-1] == dir and f.upper().startswith('D'):
            return True
    return False

def chdir(ftp, dir):
    if directory_exists(ftp, dir) is False:
        ftp.mkd(dir)
    ftp.cwd(dir)

def ftp_connection(var_date,img1):
    try: 
        connect(ftp)
        try: 
            login(ftp)
            chdir(ftp,"Object_Detection") # Change Directory

            try:            
                # Read numpy Image from PIL
                image = Image.fromarray(np.uint8(img1)).convert('RGB')
                
                # Image to Binary Mode
                temp = ioo.BytesIO() # This is a file object
                image.save(temp, format="jpeg") # Save the content to temp
                temp.seek(0) # Return the BytesIO's file pointer to the beginning of the file

                # Store image to FTP Server
                ftp.storbinary("STOR " + var_date + ".jpeg", temp)
                ftp.quit()
                IMG =  BASE_URL + var_date + ".jpeg"
                return str(IMG)
                
            except:
                print("Error in Storing Image")

        except:
            print("Login Failed.")
            
    except:
        print("No Connection.")
    


def ftp_image_url(img1):
    # Image Name Based on Current Time.
    c_time = datetime.datetime.now().today()
    date_time = c_time.strftime("%d%m%Y-%H%M%S")
    var_date = "Img"+date_time 

    ftp = ftp_connection(var_date,img1)
    
    return ftp

# Object Detection Class Names
class_names = MetadataCatalog.get(cfg.DATASETS.TRAIN[0]).thing_classes

@app.route("/",methods=['GET'])
def hello():
    return "<p>Hello, To MLOPs, I see you :v!</p>"

@app.route("/",methods=['POST'])
def objd():

    if request.method == "POST":
        list_of_urls = request.json["imageUrl"]
        results = []
        for i in list_of_urls:
            img = io.imread(i)
            im = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            # Make Prediction
            output = predictor(im)
            # Make Visualization
            v = Visualizer(im[:, :, ::-1], MetadataCatalog.get(cfg.DATASETS.TRAIN[0]), scale=1.2)
            v = v.draw_instance_predictions(output["instances"].to("cpu"))
            im1 = v.get_image()[:, :, ::-1]

            # Predicted classes and Scores
            p_classes = output['instances'].pred_classes.tolist()
            p_scores = output['instances'].scores.tolist()
            
            ftp_url = ftp_image_url(im1)

            # Prediction classes in current image
            p_class_names = list(map(lambda x: class_names[x], p_classes))
            p_scores_round = ['%.2f' % x for x in p_scores]

            results.append({"FTP_Image_URL":ftp_url,"object_classified":p_class_names,"probability_score":p_scores_round})

        return {"data": results}
    else:
        return "Error 405: Method Not Allowed"


if __name__ == "__main__":
    app.run(debug=True)
