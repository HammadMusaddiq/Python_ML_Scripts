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
from load_conf import Load_Config

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

app = Flask('LIVE_FEED')

ftp_class = Ftp_Stream()
frs_app = FRS_App()
base_url = ftp_class.getBaseURL()
ftp_cursor = ftp_class.getFTP()

# camera_ip = '192.168.23.158' , 166, 167, 199
# camera_user = 'admin'
# camera_pass = 'Rapidev@321', Admin12345

@app.route("/",methods=['GET'])
def hello():
    return "AI-Video-Anlaytics is Up and Running!" , 200


def imageToFTP(path, file_name, image_bytes):
    if str(type(image_bytes)) == "<class 'numpy.ndarray'>": # if image type is numpy array
        image = Image.fromarray(np.uint8(image_bytes)).convert('RGB')
        image_bytes = io.BytesIO() 
        image.save(image_bytes, format="png") 
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
            baseurl = baseurl + str(p) + "/"
        
        ftp_file_url = baseurl + file_name
        
        ftp_cursor.storbinary("STOR " + file_name , image_bytes)
        # ftp_cursor.quit()
        
        logger.info("Image saved on Ftp URL: "+str(ftp_file_url))

        return ftp_file_url

    except Exception as E:
        logger.error("something went wrong... Reason: {}".format(E))
        return False


def transformImage(image):
    img = Image.open(image)
    arr = np.uint8(img)

    image_shape = arr.shape
    # print("Image url shape: " + str(image_shape))
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
        
        annotated_image = cv2.rectangle(annotated_image, (box[0], box[1]), (box[2]+box[0], box[3]+box[1]), (255,0,0), 3)   #mtcnn/retinanet
        # annotated_image = cv2.rectangle(annotated_image, (box[0], box[1]), (box[2], box[3]), (255,0,0), 3)     #retinaNet
        annotated_image = cv2.putText(annotated_image, label, (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,0,0), 2)
    
    for mbox in missed_boxes:
        annotated_image = cv2.rectangle(annotated_image, (mbox[0], mbox[1]), (mbox[2]+mbox[0], mbox[3]+mbox[1]), (255,255,0), 3)   #mtcnn/retinanet
        # annotated_image = cv2.rectangle(annotated_image, (mbox[0], mbox[1]), (mbox[2], mbox[3]), (255,255,0), 3) #retinaNet
    
    return annotated_image


def sendAlert(data): # send alert to somewhere so that it can be monitored. 
    print(data)


def createVideo(image_list, image_shape, fps):
    current_timestamp = str(datetime.now().timestamp()).replace(".","")
    current_date = datetime.now().strftime('%Y%m%d')
    v_download_path = "Video_Download"
    v_complete_path = None

    if not os.path.exists(v_download_path):
        os.mkdir(v_download_path)

    if not os.path.exists(v_download_path+"/"+current_date):
        os.mkdir(v_download_path+"/"+current_date)

    if os.path.exists(v_download_path+"/"+current_date):    
        v_complete_path = v_download_path+"/"+current_date+"/"+current_timestamp+".avi"
    
        # frames to single video (How to make video from frames in custom fps and time duration)
        img_size = (image_shape[1],image_shape[0])
        # MP4V (mp4), mp4v, DIVX (avi), XVID
        out = cv2.VideoWriter(v_complete_path,cv2.VideoWriter_fourcc(*'DIVX'), int(fps), img_size)
        for i in range(len(image_list)):
            frame = cv2.cvtColor(image_list[i], cv2.COLOR_BGR2RGB)
            out.write(frame)
        out.release()
        logger.info("Video Downloaded on path " + str(v_complete_path))


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
            
        except:
            logger.error("Error 400: Bad Input")
            return "Error 400: Bad Input", 400
                
    else:
        error = "Error 405: Method Not Allowed"
        logger.error(error)
        return error, 405


def testFeed(vid):
    for i in ['first', 'second', 'third', 'fourth', 'fifth']:
        logger.info(f"No Frames detected, trying again for the {i} time.")
        time(1)
        ret, frame = vid.read()
        if ret:
            return True, frame
    return False, False


def callingFRS(frame):
    logger.info("Starting extracting embeddings.")
    embeddings, detected_boxes, recognized_boxes = frs_app.frsProcessing(frame)
    missed_boxes = extractListDiff(detected_boxes, recognized_boxes)
    matched_results = frs_app.dataExtracting(embeddings)
    return matched_results, recognized_boxes, missed_boxes


def callingSmokeDetection(image):

    node_ip, node_port, path = Load_Config().getSmokeDetection()

    files={'image': image}
    response = requests.post(f"http://{node_ip}:{node_port}/{path}",files=files) # send image as bytes with request
    print(response)


def callingWeaponDetection(image):

    node_ip, node_port, path = Load_Config().getWeaponDetection()

    files={'image': image}
    response = requests.post(f"http://{node_ip}:{node_port}/{path}",files=files) # send image as bytes with request
    print(response)


def numpyImageToBytes(numpy_image):
    image = cv2.imencode('.jpg', numpy_image)[1].tobytes() # numpy to bytes
    return image


def saveToFTP(frame, annotated_image, save_image, save_annotated_image):
    image_link = ""
    annotated_image_link = ""

    file_name = filename(None)
    current_date = datetime.now().strftime('%Y%m%d')
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    if save_image == 'True':
        image_link = imageToFTP("/AI_Video_Analytics/Camera_Feed/Images/"+str(current_date), file_name, frame)
    
    if save_annotated_image == 'True':
        annotated_image_link = imageToFTP("/AI_Video_Analytics/Camera_Feed/Annotated_Images/"+str(current_date),file_name, annotated_image)

    return image_link, annotated_image_link


def readingFrames(selected_frames, frame, frames_list, counter, iteration_count, save_image, save_annotated_image):
    recognized_boxes_all = []
    missed_boxes_all = []
    image_link = ""
    annotated_image_link = ""
    annotated_image = None
    processed_image = None

    if counter in selected_frames:
        matched_results, recognized_boxes, missed_boxes = callingFRS(frame)

        recognized_boxes_all.extend(recognized_boxes)
        missed_boxes_all.extend(missed_boxes)

        # import pdb; pdb.set_trace()
        if matched_results['detected_person'] != []:
            annotated_image = plotAnnotation(recognized_boxes_all, missed_boxes_all, matched_results['detected_person'], frame)
            processed_image = annotated_image
        
        else:
            processed_image = frame

        if save_image == 'True' or save_annotated_image == 'True':
            image_link, annotated_image_link = saveToFTP(frame, annotated_image, save_image, save_annotated_image)

        
        frames_list.append(processed_image)
        matched_results['image_link'] = image_link
        matched_results['annotated_image_link'] = annotated_image_link
        matched_results['current_time'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
              
    counter += 1
    iteration_count += 1
    return matched_results, processed_image


def readFps(total_fps, camera_fps):
    frame_no = []
    frame_jump = total_fps/int(camera_fps)

    for i in range(0,25, (round(frame_jump))):
        if len(frame_no) != camera_fps:
            frame_no.append(i)   
    return frame_no


def liveFeedOperations(live_feed, camera_fps, video_chunk, save_image, save_annotated_image, live_screen):
    counter = 0
    iteration_count = 0
    frame_shape = None
    frames_list = []
    total_fps = 25

    selected_frames = readFps(total_fps, camera_fps)
    video_chunk = int(video_chunk)*len(selected_frames) # video_chunk = seconds * fps

    vid = cv2.VideoCapture(live_feed, cv2.CAP_FFMPEG)
    while vid.isOpened():   
        ret, frame = vid.read()
        
        # if frame is read correctly ret is True
        if not ret:
            ret, frame = testFeed(vid)
            if not ret:
                logger.info(f"No Frames detected, process exiting.")
                break
        
        if not frame_shape:
            print("Program running...")
            frame_shape = frame.shape
        
        matched_results, processed_image = readingFrames(selected_frames, frame, frames_list, counter, iteration_count, save_image, save_annotated_image)
        
        # generate alerts
        sendAlert(matched_results)
        
        # create video
        if len(frames_list) == int(video_chunk):
            print("Generating video...")
            createVideo(frames_list, frame_shape, camera_fps)
            frames_list = []
        
        if counter == total_fps - 1:
            counter = 0

        if live_screen == 'True':
            cv2.imshow("Live Feed", processed_image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    vid.release()
    cv2.destroyAllWindows()

    return "No more frames, Process Finished: Total iterations " + str(iteration_count)


@app.route("/search",methods=['POST'])
def search_embeddings():
    if request.method == "POST":
        logger.info("AI-Video-Anlaytics Live Feed Started!")
        try:
            camera_ip = request.json["camera_ip"]
            camera_user = request.json["camera_user"]
            camera_pass = request.json["camera_pass"]
            camera_fps = request.json["camera_fps"]
            video_chunk = request.json['video_chunk']
            save_image = request.json['save_image']
            save_annotated_image = request.json['save_annotated_image']
            live_screen = request.json['live_screen']

            try:
                logger.info("AI-Video-Anlaytics Frame Searching Started!")
                # live_feed = "rtsp://"+camera_user+":"+camera_pass+"@"+camera_ip+"/camera"  # CCTV Camera (Hik Vision)
                live_feed = "rtsp://"+camera_user+":"+camera_pass+"@"+camera_ip  # CCTV Camera (Dahua)

                feedback = liveFeedOperations(live_feed, camera_fps, video_chunk, save_image, save_annotated_image, live_screen)
                
                return feedback

            except Exception as E:
                error = "An Exception Occured: {}".format(E)
                logger.error(error)
                return error,500

        except:
            logger.error("Error 400: Bad Input")
            return "Error 400: Bad Input", 400
                
    else:
        error = "Error 405: Method Not Allowed"
        logger.error(error)
        return error, 405


if __name__ == "__main__":
    app.run(debug=True)

