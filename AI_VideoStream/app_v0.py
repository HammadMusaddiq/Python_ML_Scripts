from shutil import ExecError
from unittest import result
import cv2
from datetime import datetime
from PIL import Image
import io
import numpy as np
import requests

from flask import Flask
from flask import request
from frs_stream_V1 import FRS_Stream
from milvus_stream_v0 import Milvus_Stream
from ftp_stream import Ftp_Stream

import operator
import logging
import os

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
model = FRS_Stream()
milvus = Milvus_Stream()
ftp_class = Ftp_Stream()
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
        ftp_cursor.quit()
        
        logger.info("Image saved on Ftp URL: "+str(ftp_file_url))
        logger.info('Finished with success')

        return ftp_file_url

    except Exception as E:
        logger.error("something went wrong... Reason: {}".format(E))
        return False


def plotAnnotation(bbox, image_label, image_link):
    # import pdb; pdb.set_trace()
    response = requests.get(image_link)
    img = Image.open(io.BytesIO(response.content))
    arr = np.uint8(img)

    image_shape = arr.shape
    # print("Image url shape: " + str(image_shape))
    if image_shape[2] != 3: # convering image to 3 channels for extracting embeddings
        arr = arr[:,:,:3]

    # plot annotation
    annotated_image = None
    
    if isinstance(image_label, str):
        image_label = [image_label]

    for box, label in zip(bbox,image_label):
        if label == []:
            label = "Unknown"
        annotated_image = cv2.rectangle(arr, (box[0], box[1]), (box[2]+box[0], box[3]+box[1]), (255,0,0), 3) #mtcnn/retinanet
        # annotated_image = cv2.rectangle(arr, (box[0], box[1]), (box[2], box[3]), (255,0,0), 3)     #retinaNet
        labelled_image = cv2.putText(annotated_image, label, (box[0], box[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,0,0), 2)
    
    return labelled_image


def sendAlert(data, link, time, alink): # send alert to somewhere so that it can be monitored. 
    print(data, link, time, alink)


def extractNames(images_list):
    names = []
    for lst in images_list:
        if lst == []:
            names.append([])
        else:
            url = lst[0]['url']
            name = url.split('/')[-1]
            name = name.split('_')[1]
            name = name.split('.jpg')[0]
            names.append(name)
    return names


def flatten(list_of_lists):
    if len(list_of_lists) == 0:
        return list_of_lists
    if isinstance(list_of_lists[0], list):
        return flatten(list_of_lists[0]) + flatten(list_of_lists[1:])
    return list_of_lists[:1] + flatten(list_of_lists[1:])


def createVideo(image_list, image_shape):

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
        video_fps = 2
        # MP4V (mp4), mp4v, DIVX (avi), XVID
        out = cv2.VideoWriter(v_complete_path,cv2.VideoWriter_fourcc(*'DIVX'), video_fps, img_size)
        for i in range(len(image_list)):
            frame = cv2.cvtColor(image_list[i], cv2.COLOR_BGR2RGB)
            out.write(frame)
        out.release()
        logger.info("Video Downloaded on path " + str(v_complete_path))


def pre_frs():
    current_timestamp = str(datetime.now().timestamp()).replace(".","")
    current_date = datetime.now().strftime('%Y%m%d')

    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # Store image on FTP server
    image_link = imageToFTP("/AI_Video_Analytics/Camera_Feed/"+str(current_date), current_timestamp + ".jpg", frame)
    
    logger.info("Starting extracting embeddings.")

    face_prediction = model.predict(frame)
    embeddings = face_prediction['data']
    box = face_prediction['box']

    if embeddings == 'Image Resolution is Low':
        sendAlert("Image Resolution is Low", image_link, current_timestamp, "")
        # image_frames_list.append(frame)
        # return {"matched_images": "Image Resolution is Low"}

    elif len(embeddings) != 0 and image_link != False:
        
        matched_images = []
        logger.info("Starting searching similar embeddings.")
        for emb in embeddings:
            image_list = milvus.search(emb)
            if image_list != False:
                matched_images.append(image_list)


        # box and matched_images will be in sequence so can be used to plot label on the image
        # plot axis and label on image and upload image of ftp server
    
        list_of_names = extractNames(matched_images)

        # extract names from matched_images list and send to plot annotations
        frame = plotAnnotation(box, list_of_names,image_link)
        annotated_image_link = imageToFTP("/AI_Video_Analytics/Camera_Feed/Annotated_Images"+str(current_date),current_timestamp + ".jpg", annotated_image)
        # import pdb; pdb.set_trace()
        matched_images_flatten = flatten(matched_images)
        
        if matched_images_flatten:
            # Remove duplicates based on a single key in dict
            K = "url"
            
            memo = set()
            res = []
            for sub in matched_images_flatten:
                
                # testing for already present value
                if sub[K] not in memo:
                    res.append(sub)
                    
                    # adding in memo if new value
                    memo.add(sub[K])

            logger.info("Matched images has been extracted, process completed with success.")
            
            result = {"matched_images":sorted(res, key=operator.itemgetter('distance'), reverse=False)}
            sendAlert(result, image_link, current_timestamp, annotated_image_link)

            # return  {"matched_images":sorted(res, key=operator.itemgetter('distance'), reverse=False)} # list of (list of dictionary) if matched otherwise []
        
        elif matched_images_flatten == [] and image_list != False: # if no image matched
            logger.info("No matched image found, process completed with success.")
            sendAlert([], image_link, current_timestamp, annotated_image_link)
            # return {"matched_images":[]}

        else: # returing false, means searching failed on milvus database 
            sendAlert(False, image_link, current_timestamp, annotated_image_link)
            # return False
    
        
        # image_frames_list.append(annotated_image)


    else: # no face found or error on FTP
        # image_frames_list.append(frame)
        sendAlert([], image_link, current_timestamp, "")



                       
@app.route("/insert",methods=['POST'])
def insert_embeddings():
    if request.method == "POST":
        logger.info("AI-Video-Anlaytics Image Inserting Started!")
        try:
            image = request.files['image_path']
            person_name = request.form['person_name']

            try:
                ctime = str(datetime.now().timestamp()).replace(".","")
                logger.info("Time: "+str(ctime))
                
                # Store image on FTP server
                file_name = str(ctime) + "_" + person_name + ".jpg"
                image_link = imageToFTP("/AI_Video_Analytics/Image_Upload/Images", file_name, image)

                face_prediction = model.predict(image)
                embeddings = face_prediction['embeddings']
                box = face_prediction['recognized_boxes']       

                if embeddings == 'Image Resolution is Low':
                    return {"milvus_id": "Image Resolution is Low"}

                elif len(embeddings) != 0 and image_link != False:
                
                    # plot axis on image and upload image of ftp server
                    annotated_image = plotAnnotation(box, person_name, image_link)
                    annotated_image_link = imageToFTP("/AI_Video_Analytics/Image_Upload/Annotated_Images",file_name, annotated_image)

                    milvus_ids = []
                    box_axis = []

                    logger.info("Starting inserting embeddings in the Milvus DB.")
                    for emb,bx in zip(embeddings,box):
                        idx = milvus.insert(emb)
                        if idx:
                            milvus_ids.append(idx)
                            box_axis.append([int(val) for val in bx])
                    
                    # import pdb; pdb.set_trace()
                    if milvus_ids:
                        check = milvus.dumpToElasticSearch(milvus_ids,box_axis,image_link, annotated_image_link)
                        if check == True:
                            logger.info("Milvus ID has been saved in ES, Process completed with success.")
                            return {"milvus_id":milvus_ids} # milvus ids of all extracted faces embeddings

                    else: # returing false, means embeddings not saved on milvus database
                        return False

                else:
                    return {"milvus_id": []}


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



@app.route("/search",methods=['POST'])
def search_embeddings():
    if request.method == "POST":
        try:
            logger.info("AI-Video-Anlaytics Live Feed Started!")
            image = request.files['image_path']
            try:
                logger.info("AI-Video-Anlaytics Frame Searching Started!")

                current_timestamp = str(datetime.now().timestamp()).replace(".","")

                # Store image on FTP server
                # image_link = imageToFTP("/AI_Video_Analytics/Camera_Feed/"+str(current_date), current_timestamp + ".jpg", image)
                
                logger.info("Starting extracting embeddings.")

                face_prediction = model.predict(image)
                embeddings = face_prediction['embeddings']
                box = face_prediction['recognized_boxes']
                result = []

                if embeddings == 'Image Resolution is Low':
                    print("Image Resolution is Low", "", current_timestamp, "")

                # elif len(embeddings) != 0 and image_link != False:
                elif len(embeddings) != 0:
                    
                    matched_images = []
                    logger.info("Starting searching similar embeddings.")
                    # import pdb; pdb.set_trace()
                    for emb in embeddings:
                        image_list = milvus.search(emb)
                        if image_list != False:
                            matched_images.append(image_list)



                
                    list_of_names = extractNames(matched_images)
                    print(list_of_names)

                    # extract names from matched_images list and send to plot annotations
                    # annotated_image = plotAnnotation(box, list_of_names,image_link)
                    # annotated_image_link = imageToFTP("/AI_Video_Analytics/Camera_Feed/Annotated_Images"+str(current_date),current_timestamp + ".jpg", annotated_image)
                    matched_images_flatten = flatten(matched_images)
                    
                    if matched_images_flatten:
                        # Remove duplicates based on a single key in dict
                        K = "url"
                        
                        memo = set()
                        res = []
                        for sub in matched_images_flatten:
                            
                            # testing for already present value
                            if sub[K] not in memo:
                                res.append(sub)
                                
                                # adding in memo if new value
                                memo.add(sub[K])

                        logger.info("Matched images has been extracted, process completed with success.")
                        
                        result = {"matched_images":sorted(res, key=operator.itemgetter('distance'), reverse=False)}
                        print(result, "image_link", current_timestamp, "annotated_image_link")

                        # return  {"matched_images":sorted(res, key=operator.itemgetter('distance'), reverse=False)} # list of (list of dictionary) if matched otherwise []
                    
                    elif matched_images_flatten == [] and image_list != False: # if no image matched
                        logger.info("No matched image found, process completed with success.")
                        print([], "image_link", current_timestamp, "annotated_image_link")
                        # return {"matched_images":[]}

                    else: # returing false, means searching failed on milvus database 
                        sendAlert(False, "image_link", current_timestamp, "annotated_image_link")
                        # return False

                else: # no face found or error on FTP
                    print([], "image_link", current_timestamp, "")

                return result
                
            except Exception as E:
                error = "An Exception Occured: {}".format(E)
                logger.error(error)
                return error,500


        except Exception as E:
            print(E)
            logger.error("Error 400: Bad Input")
            return "Error 400: Bad Input", 400

                
    else:
        error = "Error 405: Method Not Allowed"
        logger.error(error)
        return error, 405





if __name__ == "__main__":
    app.run(debug=False)



# @app.route("/search",methods=['POST'])
# def search_embeddings():
#     if request.method == "POST":
#         try:
#             logger.info("AI-Video-Anlaytics Live Feed Started!")
#             camera_ip = request.json["camera_ip"]
#             camera_user = request.json["camera_user"]
#             camera_pass = request.json["camera_pass"]

#             try:
#                 logger.info("AI-Video-Anlaytics Frame Searching Started!")
#                 # live_feed = "rtsp://"+camera_user+":"+camera_pass+"@"+camera_ip+"/camera"  # CCTV Camera
#                 live_feed = "rtsp://"+camera_user+":"+camera_pass+"@"+camera_ip  # CCTV Camera

#                 counter = 0
#                 frame_counter = 0
#                 image_frames_list = []
#                 image_frames_shape = None
#                 iteration_count = 0

#                 vid = cv2.VideoCapture(live_feed, cv2.CAP_FFMPEG)
#                 while vid.isOpened():   
#                     ret, frame = vid.read()
                    
#                     # if frame is read correctly ret is True
#                     if not ret:
#                         logger.info("No Frames, Process exiting.")
#                         break
                    
#                     if counter ==5 or counter == 15:

#                         image_frames_shape = frame.shape
#                         # print(image_frames_shape)
                        
#                         if counter == 15:
#                             counter=0
                        
#                         print("Reading Frame...")  

#                         # current_timestamp = str(datetime.now()).replace(' ','_').replace('-','').replace(':','').split('.')[0]
#                         # idx = current_timestamp+'_'+str(frame_counter)
                        
#                         if frame_counter == 1:
#                             frame_counter=0
#                         else:
#                             frame_counter += 1


#                         current_timestamp = str(datetime.now().timestamp()).replace(".","")
#                         current_date = datetime.now().strftime('%Y%m%d')

#                         frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

#                         # Store image on FTP server
#                         image_link = imageToFTP("/AI_Video_Analytics/Camera_Feed/"+str(current_date), current_timestamp + ".jpg", frame)
                        
#                         logger.info("Starting extracting embeddings.")

#                         face_prediction = model.predict(frame)
#                         embeddings = face_prediction['data']
#                         box = face_prediction['box']

#                         if embeddings == 'Image Resolution is Low':
#                             sendAlert("Image Resolution is Low", image_link, current_timestamp, "")
#                             image_frames_list.append(frame)
#                             # return {"matched_images": "Image Resolution is Low"}

#                         elif len(embeddings) != 0 and image_link != False:
                            
#                             matched_images = []
#                             logger.info("Starting searching similar embeddings.")
#                             for emb in embeddings:
#                                 image_list = milvus.search(emb)
#                                 if image_list != False:
#                                     matched_images.append(image_list)


#                             # box and matched_images will be in sequence so can be used to plot label on the image
#                             # plot axis and label on image and upload image of ftp server
                        
#                             list_of_names = extractNames(matched_images)

#                             # extract names from matched_images list and send to plot annotations
#                             annotated_image = plotAnnotation(box, list_of_names,image_link)
#                             annotated_image_link = imageToFTP("/AI_Video_Analytics/Camera_Feed/Annotated_Images"+str(current_date),current_timestamp + ".jpg", annotated_image)
#                             # import pdb; pdb.set_trace()
#                             matched_images_flatten = flatten(matched_images)
                            
#                             if matched_images_flatten:
#                                 # Remove duplicates based on a single key in dict
#                                 K = "url"
                                
#                                 memo = set()
#                                 res = []
#                                 for sub in matched_images_flatten:
                                    
#                                     # testing for already present value
#                                     if sub[K] not in memo:
#                                         res.append(sub)
                                        
#                                         # adding in memo if new value
#                                         memo.add(sub[K])

#                                 logger.info("Matched images has been extracted, process completed with success.")
                                
#                                 result = {"matched_images":sorted(res, key=operator.itemgetter('distance'), reverse=False)}
#                                 sendAlert(result, image_link, current_timestamp, annotated_image_link)

#                                 # return  {"matched_images":sorted(res, key=operator.itemgetter('distance'), reverse=False)} # list of (list of dictionary) if matched otherwise []
                            
#                             elif matched_images_flatten == [] and image_list != False: # if no image matched
#                                 logger.info("No matched image found, process completed with success.")
#                                 sendAlert([], image_link, current_timestamp, annotated_image_link)
#                                 # return {"matched_images":[]}

#                             else: # returing false, means searching failed on milvus database 
#                                 sendAlert(False, image_link, current_timestamp, annotated_image_link)
#                                 # return False
                        
                            
#                             image_frames_list.append(annotated_image)


#                         else: # no face found or error on FTP
#                             image_frames_list.append(frame)
#                             sendAlert([], image_link, current_timestamp, "")

#                         iteration_count += 1

                        
#                     # create video
#                     if len(image_frames_list) == 20:
#                         print("Generating Video...")
#                         createVideo(image_frames_list, image_frames_shape)
#                         image_frames_list = []
                
#                     counter += 1
#                     # iteration_count += 1

#                 vid.release()
#                 cv2.destroyAllWindows()

#                 return "Process Finished: Total iterations " + str(iteration_count)


#             except Exception as E:
#                 error = "An Exception Occured: {}".format(E)
#                 logger.error(error)
#                 return error,500


#         except:
#             logger.error("Error 400: Bad Input")
#             return "Error 400: Bad Input", 400

                
#     else:
#         error = "Error 405: Method Not Allowed"
#         logger.error(error)
#         return error, 405




# @app.route("/search",methods=['POST'])
# def search_embeddings():
#     if request.method == "POST":
#         try:
#             logger.info("AI-Video-Anlaytics Live Feed Started!")
#             camera_ip = request.json["camera_ip"]
#             camera_user = request.json["camera_user"]
#             camera_pass = request.json["camera_pass"]

#             try:
#                 logger.info("AI-Video-Anlaytics Frame Searching Started!")
#                 # live_feed = "rtsp://"+camera_user+":"+camera_pass+"@"+camera_ip+"/camera"  # CCTV Camera
#                 live_feed = "rtsp://"+camera_user+":"+camera_pass+"@"+camera_ip  # CCTV Camera

#                 counter = 0
#                 frame_counter = 0
#                 image_frames_list = []
#                 image_frames_shape = None
#                 iteration_count = 0

#                 vid = cv2.VideoCapture(live_feed, cv2.CAP_FFMPEG)
#                 while vid.isOpened():   
#                     ret, frame = vid.read()
                    
#                     # if frame is read correctly ret is True
#                     if not ret:
#                         logger.info("No Frames, Process exiting.")
#                         break
                    
#                     if counter ==5 or counter == 15:

#                         image_frames_shape = frame.shape
#                         # print(image_frames_shape)
                        
#                         if counter == 15:
#                             counter=0
                        
#                         print("Reading Frame...")  

#                         # current_timestamp = str(datetime.now()).replace(' ','_').replace('-','').replace(':','').split('.')[0]
#                         # idx = current_timestamp+'_'+str(frame_counter)
                        
#                         if frame_counter == 1:
#                             frame_counter=0
#                         else:
#                             frame_counter += 1


#                         current_timestamp = str(datetime.now().timestamp()).replace(".","")
#                         current_date = datetime.now().strftime('%Y%m%d')

#                         frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

#                         # Store image on FTP server
#                         image_link = imageToFTP("/AI_Video_Analytics/Camera_Feed/"+str(current_date), current_timestamp + ".jpg", frame)
                        
#                         logger.info("Starting extracting embeddings.")

#                         face_prediction = model.predict(frame)
#                         embeddings = face_prediction['data']
#                         box = face_prediction['box']

#                         if embeddings == 'Image Resolution is Low':
#                             sendAlert("Image Resolution is Low", image_link, current_timestamp, "")
#                             image_frames_list.append(frame)
#                             # return {"matched_images": "Image Resolution is Low"}

#                         elif len(embeddings) != 0 and image_link != False:
                            
#                             matched_images = []
#                             logger.info("Starting searching similar embeddings.")
#                             for emb in embeddings:
#                                 image_list = milvus.search(emb)
#                                 if image_list != False:
#                                     matched_images.append(image_list)


#                             # box and matched_images will be in sequence so can be used to plot label on the image
#                             # plot axis and label on image and upload image of ftp server
                        
#                             list_of_names = extractNames(matched_images)

#                             # extract names from matched_images list and send to plot annotations
#                             annotated_image = plotAnnotation(box, list_of_names,image_link)
#                             annotated_image_link = imageToFTP("/AI_Video_Analytics/Camera_Feed/Annotated_Images"+str(current_date),current_timestamp + ".jpg", annotated_image)
#                             # import pdb; pdb.set_trace()
#                             matched_images_flatten = flatten(matched_images)
                            
#                             if matched_images_flatten:
#                                 # Remove duplicates based on a single key in dict
#                                 K = "url"
                                
#                                 memo = set()
#                                 res = []
#                                 for sub in matched_images_flatten:
                                    
#                                     # testing for already present value
#                                     if sub[K] not in memo:
#                                         res.append(sub)
                                        
#                                         # adding in memo if new value
#                                         memo.add(sub[K])

#                                 logger.info("Matched images has been extracted, process completed with success.")
                                
#                                 result = {"matched_images":sorted(res, key=operator.itemgetter('distance'), reverse=False)}
#                                 sendAlert(result, image_link, current_timestamp, annotated_image_link)

#                                 # return  {"matched_images":sorted(res, key=operator.itemgetter('distance'), reverse=False)} # list of (list of dictionary) if matched otherwise []
                            
#                             elif matched_images_flatten == [] and image_list != False: # if no image matched
#                                 logger.info("No matched image found, process completed with success.")
#                                 sendAlert([], image_link, current_timestamp, annotated_image_link)
#                                 # return {"matched_images":[]}

#                             else: # returing false, means searching failed on milvus database 
#                                 sendAlert(False, image_link, current_timestamp, annotated_image_link)
#                                 # return False
                        
                            
#                             image_frames_list.append(annotated_image)


#                         else: # no face found or error on FTP
#                             image_frames_list.append(frame)
#                             sendAlert([], image_link, current_timestamp, "")

#                         iteration_count += 1

                        
#                     # create video
#                     if len(image_frames_list) == 20:
#                         print("Generating Video...")
#                         createVideo(image_frames_list, image_frames_shape)
#                         image_frames_list = []
                
#                     counter += 1
#                     # iteration_count += 1

#                 vid.release()
#                 cv2.destroyAllWindows()

#                 return "Process Finished: Total iterations " + str(iteration_count)


#             except Exception as E:
#                 error = "An Exception Occured: {}".format(E)
#                 logger.error(error)
#                 return error,500


#         except:
#             logger.error("Error 400: Bad Input")
#             return "Error 400: Bad Input", 400

                
#     else:
#         error = "Error 405: Method Not Allowed"
#         logger.error(error)
#         return error, 405




# @app.route("/search",methods=['POST'])
# def search_embeddings():
#     # import pdb;pdb.set_trace()
#     if request.method == "POST":
#         try:
#             logger.info("AI-Video-Anlaytics Live Feed Started!")
            
#             image = request.files['image']

#             try:
#                 logger.info("AI-Video-Anlaytics Frame Searching Started!")

#                 current_timestamp = str(datetime.now().timestamp()).replace(".","") + ".jpg"
#                 current_date = datetime.now().strftime('%Y%m%d')


    
#                 # Store image on FTP server
#                 image_link = imageToFTP("/AI_Video_Analytics/Camera_Feed/"+str(current_date), current_timestamp, image)                       
                        
#                 logger.info("Starting extracting embeddings.")
#                 face_prediction = model.predict(image)
#                 embeddings = face_prediction['data']
#                 box = face_prediction['box']

#                 if embeddings == 'Image Resolution is Low':
#                     sendAlert("Image Resolution is Low", image_link, current_timestamp, "")
#                     # return {"matched_images": "Image Resolution is Low"}

#                 elif len(embeddings) != 0 and image_link != False:
        
#                     # plot axis on image and upload image of ftp server
#                     annotated_image = plotAnnotation(box, image_link)
#                     annotated_image_link = imageToFTP("/AI_Video_Analytics/Camera_Feed/Annotated_Images"+str(current_date),current_timestamp, annotated_image)
                    
#                     matched_images = []
#                     logger.info("Starting searching similar embeddings.")
#                     for emb in embeddings:
#                         image_list = milvus.search(emb)
#                         if image_list != False:
#                             matched_images.extend(image_list)
                    
#                     #import pdb;pdb.set_trace()
#                     if matched_images:
#                         # Remove duplicates based on a single key in dict
#                         K = "url"
                        
#                         memo = set()
#                         res = []
#                         for sub in matched_images:
                            
#                             # testing for already present value
#                             if sub[K] not in memo:
#                                 res.append(sub)
                                
#                                 # adding in memo if new value
#                                 memo.add(sub[K])

#                         logger.info("Matched images has been extracted, process completed with success.")
                        
#                         result = {"matched_images":sorted(res, key=operator.itemgetter('distance'), reverse=False)}
#                         sendAlert(result, image_link, current_timestamp, annotated_image_link)
                        
#                         # return  {"matched_images":sorted(res, key=operator.itemgetter('distance'), reverse=False)} # list of (list of dictionary) if matched otherwise []
                    
#                     elif matched_images == [] and image_list != False: # if no image matched
#                         logger.info("No matched image found, process completed with success.")
#                         sendAlert([], image_link, current_timestamp, annotated_image_link)
#                         # return {"matched_images":[]}

#                     else: # returing false, means searching failed on milvus database
#                         sendAlert(False, image_link, current_timestamp, annotated_image_link)
#                         # return False
                            
#                 else:
#                     sendAlert([], image_link, current_timestamp, "")
                    
#                 cv2.destroyAllWindows()


#             except Exception as E:
#                 error = "An Exception Occured: {}".format(E)
#                 logger.error(error)
#                 return error,500


#         except:
#             logger.error("Error 400: Bad Input")
#             return "Error 400: Bad Input", 400

                
#     else:
#         error = "Error 405: Method Not Allowed"
#         logger.error(error)
#         return error, 405


# if __name__ == "__main__":
#     app.run(debug=False)
