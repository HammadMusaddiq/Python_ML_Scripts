from pyspark.sql.functions import udf

import random
import requests
import numpy as np

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, ArrayType

import matplotlib.patheffects as PathEffects
import matplotlib.pyplot as plt
from matplotlib import patches, text, patheffects
from matplotlib.backends.backend_agg import FigureCanvasAgg

import datetime
import io
from skimage import io as io_skimage
import configparser
from ftplib import FTP

import collections
import os, shutil
import cv2
from PIL import Image
import math
import matplotlib as mpl
import sys
import es_pyspark_handler

GTR = sys.argv[1]
CTR = sys.argv[2]
target_type = sys.argv[3]
target_subtype = sys.argv[4]

if os.path.isdir("ObjectDetectionFrames") == False:
    os.mkdir("ObjectDetectionFrames")

# For access path, on cluster user this ("hdfs:///user/config/config.ini"). on System user this ("hdfs://192.168.18.182/user/config/config.ini")
conf_path = "hdfs:///user/config/config.ini"

# configuration for FTP
node_ip_ftp = None
node_port_ftp = None
auth_user_ftp  = None
auth_pass_ftp  = None

# configuration for OBJD_FLASK
node_ip_objd = None
node_port_objd = None

def initialize_config(spark):
    global node_ip_ftp 
    global node_port_ftp 
    global auth_user_ftp 
    global auth_pass_ftp 

    global node_ip_objd
    global node_port_objd 

    parse_str = configparser.ConfigParser()
    c = spark.sparkContext.textFile(conf_path).collect()
    buf = io.StringIO("\n".join(c))
    x = parse_str.readfp(buf)
    node_ip_ftp = str(parse_str.get('FTP', 'host')).strip()
    node_port_ftp = str(parse_str.get('FTP', 'port')).strip()
    auth_user_ftp = str(parse_str.get('FTP', 'username')).strip()
    auth_pass_ftp = str(parse_str.get('FTP', 'password')).strip()

    node_ip_objd = str(parse_str.get('OBJD_FLASK', 'ip')).strip()
    node_port_objd = str(parse_str.get('OBJD_FLASK', 'port')).strip()

colors  = ['antiquewhite', 'aqua', 'aquamarine', 'bisque', 'black', 'blanchedalmond', 'blue', 'blueviolet', 'brown', 'burlywood', 'cadetblue', 'chartreuse', 'chocolate', 'coral', 'cornflowerblue', 'cornsilk', 'crimson', 'cyan', 'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgray', 'darkgreen', 'darkgrey', 'darkkhaki', 'darkmagenta', 'darkolivegreen', 'darkorange', 'darkorchid', 'darkred', 'darksalmon', 'darkseagreen', 'darkslateblue', 'darkslategray', 'darkslategrey', 'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue', 'dimgray', 'dimgrey', 'dodgerblue', 'firebrick', 'forestgreen', 'fuchsia', 'gainsboro', 'gold', 'goldenrod', 'gray', 'green', 'greenyellow', 'grey', 'hotpink', 'indianred', 'indigo', 'khaki', 'lawngreen', 'lemonchiffon', 'lightblue', 'lightcoral', 'lightgray', 'lightgreen', 'lightgrey', 'lightpink', 'lightsalmon', 'lightseagreen', 'lightskyblue', 'lightslategray', 'lightslategrey', 'lightsteelblue', 'lime', 'limegreen', 'magenta', 'maroon', 'mediumaquamarine', 'mediumblue', 'mediumorchid', 'mediumpurple', 'mediumseagreen', 'mediumslateblue', 'mediumspringgreen', 'mediumturquoise', 'mediumvioletred', 'midnightblue', 'mistyrose', 'moccasin', 'navajowhite', 'navy', 'olive', 'olivedrab', 'orange', 'orangered', 'orchid', 'palegoldenrod', 'palegreen', 'paleturquoise', 'palevioletred', 'papayawhip', 'peachpuff', 'peru', 'pink', 'plum', 'powderblue', 'purple', 'rebeccapurple', 'red', 'rosybrown', 'royalblue', 'saddlebrown', 'salmon', 'sandybrown', 'seagreen', 'sienna', 'silver', 'skyblue', 'slateblue', 'slategray', 'slategrey', 'springgreen', 'steelblue', 'tan', 'teal', 'thistle', 'tomato', 'turquoise', 'violet', 'wheat', 'yellow', 'yellowgreen']

spark = SparkSession.builder.getOrCreate()

initialize_config(spark)

elastic_index = "_".join([target_type, target_subtype, "posts"])

df = es_pyspark_handler.search_col_by_index_fields_and_type(spark, elastic_index, GTR, columns="GTR,CTR,posts.media_c,posts.id",array_cols="posts.media_c")
print(df.printSchema())
print(df.show())
df = df.withColumn("target_type",lit(target_type))\
        .withColumn("target_subtype",lit(target_subtype))

# #**************************

# video_urls = ['http://192.168.18.33/osint_system/media_files/Object_Detection_Video/video-road1.mp4']

# df = spark.createDataFrame(video_urls, StringType())
# df = df.selectExpr("value as Video_Links")

# # df = spark.read.json("hdfs://192.168.18.182/user/Hammad/st_fb_7078.json")
# # df = df.select('content.posts','target_information.CTR', 'target_information.GTR', 'target_information.target_subtype','target_information.target_type')
# # df = df.select('CTR','GTR','target_type','target_subtype','posts.media_c')
# # print(df.printSchema())

# #**************************


BASE_URL = "http://"+node_ip_ftp+"/osint_system/media_files/Object_Detection_Video/"
#print(BASE_URL)

# Method of calling model configuation from DetectronApp using Flask App
def callConfig():
    headers = {
        "Content-Type":"application/json"
    }
    cfg = requests.get(f"http://{node_ip_objd}:{node_port_objd}/get_config",headers=headers).json()
    return cfg['config']

model_cfg = callConfig()

# FTP Server Connection
ftp = None
def connect():
    global ftp
    ftp = FTP()
    try:
        ftp.connect(node_ip_ftp, int(node_port_ftp))
        return True
    except Exception as e:
        print(e)
        return False

def login():
    global ftp
    try:
        ftp.login(auth_user_ftp, auth_pass_ftp)
        return True
    except Exception as e:
        print(e)
        return False

def directory_exists(dir):
    global ftp
    filelist = []
    ftp.retrlines('LIST', filelist.append)
    #print(filelist)
    for f in filelist:
        if f.split()[-1] == dir and f.upper().startswith('D'):
            return True
    return False

def chdir(dir):
    global ftp
    if directory_exists(dir) is False:
        ftp.mkd(dir)
    ftp.cwd(dir)

def emptyFTPDir():
    dirname = 'Object_Detection_Video/Frames'
    try: 
        connect()
        try: 
            login()
            #chdir("Object_Detection_Video")
            #chdir("Frames")
            ftp.cwd(dirname)
            try:
                # print(ftp.nlst())
                for file in ftp.nlst():
                    try:
                        ftp.delete(file) # Delete Files
                    except Exception:
                        ftp.rmd(file) # Delete Folder
                ftp.quit()
            except Exception as E:
                print(E)
        except Exception as E:
            print(E)
    except Exception as E:
        print(E)

# Video to Frames
def vidToFrames(video_url):
    # Image based on each second (Framerate - FPS) (Custom Setting of FPS) (object detection on frames)
    read_video = cv2.VideoCapture(video_url)

    frameRate = 0.1 #it will capture image in each 1 second (10 images per second)- 10 FPS
    sec = 0.0
    count = 0
    img_array = []
    img_url_ftp = []

    while read_video.isOpened():
        sec = round(sec, 2)
        read_video.set(cv2.CAP_PROP_POS_MSEC,sec*1000) 
        ret, frame = read_video.read()
        
        # if frame is read correctly ret is True
        if not ret:
            break

        count = count + 1

        decimal_part, number_part  = math.modf(sec)
        image_name = 'VidSecond'+str(int(number_part))+'Frame'+str(count)
        
        cvt_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        image = Image.fromarray(np.uint8(cvt_frame)).convert('RGB')

        sec = sec + frameRate
        
        image_link = ftp_connection(image_name, image)
        
        #img_array.append(frame)
        img_url_ftp.append(image_link)
        
        height, width, layers = frame.shape
        img_size = (width,height)
        
        if count == 10: # 10 Frames for image name
            count = 0

        if cv2.waitKey(1) == ord('q'):
            break

    # read_video.release()
    # cv2.destroyAllWindows()
    return img_size, img_url_ftp

# Image to FTP
def ftp_connection(img_name,img_source):
    try: 
        connect()
        try: 
            login()
            chdir("Object_Detection_Video")  # Change Directory
            try:

                if isinstance(img_source, str):     # For Video it has path name in string
                    print("Storing Video on FTP")
                    file = open(img_source,'rb')   # "rb" (reading the local file in binary mode)

                    ftp.storbinary("STOR " + img_name + ".mp4", file)
                    ftp.quit()
                    file.close()
                    IMG_Path =  BASE_URL + img_name + ".mp4"

                else:   # For pictures/Frames it is numpy
                    chdir("Frames")
                    temp = io.BytesIO() # This is a file object
                    img_source.save(temp, format="jpeg") # For PIL Image
                    #img_source.savefig(temp, format="jpeg",bbox_inches='tight',pad_inches = 0) # Save the content to temp, for Matplot Image
                    temp.seek(0) # Return the BytesIO's file pointer to the beginning of the file

                    ftp.storbinary("STOR " + img_name + ".jpeg", temp)
                    ftp.quit()
                    temp.close()
                    IMG_Path =  BASE_URL + "Frames/" + img_name + ".jpeg"

                return str(IMG_Path)

            except Exception as E:
                print(E)

        except Exception as E:
            print(E)

    except Exception as E:
        print(E)

def plot_Image_Boundings(objd_data,img,image_size):
    # converting str list to flost list
    objd_data_predicted_axis = []
    for axis in objd_data['predicted_axis']:
        objd_data_predicted_axis.append([float(val) for val in axis])

    if objd_data_predicted_axis: # If object(s) found in the image/frame
        height, width = image_size
        # Pixels to Inches for Matplotlib
        height = height * 0.0104166667
        width = width * 0.0104166667

        fig = plt.figure(figsize=(height,width),facecolor='Black')
        ax = fig.add_axes([0.0, 0.0, 1.0, 1.0], alpha=1.0)
        ax.set_frame_on(False)
        ax.set_xticks([])
        ax.set_yticks([])

        box_axis = []
        box_text = []
        box_color = []
        for _box,_score,_class in zip(objd_data_predicted_axis,objd_data['probability_score'],objd_data['object_classified']):
            x1, y1, x2, y2 = tuple(_box)    # xmin, ymin, xmax, ymax (x is Top, y is Left)
            # print(x1,y1,x2,y2)
            w, h = x2 - x1, y2 - y1  # width (w) = xmax - xmin ; height (h) = ymax - ymin (w is Right, h is Bottom)

            random_color = colors[random.randrange(0,len(colors) - 1)]
            box_color.extend([random_color])
            box_axis.append([mpl.patches.Rectangle((x1,y1),w,h, fill=False, color=random_color, lw=3)])
            box_text.append([x1+2, (y1+2), str(_class+' ('+_score+'%)')])

        for axis,b_text,b_color in zip(box_axis,box_text,box_color):
            for rectangle in axis:
                ax.add_patch(rectangle)

            text_x,text_y,text_s = b_text
            t = ax.text(text_x, text_y, text_s, verticalalignment='top', color="white", fontsize=8, weight='bold')
            t.set_bbox(dict(facecolor=b_color, alpha=0.4, edgecolor='black'))
            t.set_path_effects([PathEffects.withStroke(linewidth=1,foreground="black")])
            
        ax.get_xaxis().set_visible(False)
        ax.imshow(img)

        image = fig
        plt.close(fig)

        return True, image   # fig/image has image object (RGB)

    else:       # If no object found in the image, img is numpy array of actual image
        return False, img 
    
    # image_name = "Img"+str(datetime.datetime.now().timestamp()).replace(".","")
    # plt.savefig('ObjectDetectionFrames/'+image_name, format="jpeg",bbox_inches='tight',pad_inches = 0) # Save the content to temp, for Matplot Image
    

def imageToNumpy(fig):

    #plt.show()

    # First need to draw Figure
    fig.canvas.draw()
    # Now we can save it to a numpy array.
    img_canvas_arr = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    img_canvas_arr = img_canvas_arr.reshape(fig.canvas.get_width_height()[::-1] + (3,))

    img_array_rgb = cv2.cvtColor(img_canvas_arr, cv2.COLOR_RGB2BGR)

    height1, width1, layers1 = img_array_rgb.shape # use this shape/size
    img_size = (width1,height1)
    
    return img_array_rgb, img_size

def videoToFTP(img_array,size):

    # Frames to Video with Custom FPS
    video_fps = 10
    #print(size)

    out2 = cv2.VideoWriter('Object_Detection_Output_Video.mp4',cv2.VideoWriter_fourcc(*'mp4v'), video_fps, size)
    #print("Frames array Lenght: " + str(len(img_array)))
    for i in range(len(img_array)):
        out2.write(img_array[i])
    out2.release()
    
    vid_path = "Object_Detection_Output_Video.mp4"

    vid_name = "Vid"+str(datetime.datetime.now().timestamp()).replace(".","")
    video_path = ftp_connection(vid_name,vid_path)

    # To remove/delete saved video from local directory
    # if os.path.exists("Object_Detection_Output_Video.mp4"):
    #     os.remove("Object_Detection_Output_Video.mp4")
    
    return video_path

def objClassified(objects, scores):

    # converting str list to flost list of scores
    score_to_float = []
    for values in scores:
        score_to_float.append(float(values))

    occurrences = collections.Counter(objects)
    obj_count = occurrences.values() # Count the occurance of same objects

    sums = {} # Sum the values on two lists based on same objects
    for key, value in zip(objects,score_to_float):
        try:
            sums[key] = sums[key] + value
        except KeyError:
            sums[key] = value

    obj_keys = sums.keys()
    obj_score = sums.values()

    obj_key_lst = []
    for i in obj_keys:
        obj_key_lst.append(i)

    obj_sco_lst = [] # Only need average of the score
    for j in obj_score:
        obj_sco_lst.append(j)
 
    obj_cnt_lst = []
    for k in obj_count:
        obj_cnt_lst.append(k)

    obj_score_avg = [] # So from here we are getting the average of the score
    for key, value in zip(obj_sco_lst,obj_cnt_lst):
        obj_score_avg.append(key/value)

    return obj_key_lst, obj_cnt_lst, obj_score_avg

# Object Detection Schema
schema_obj_detection = StructType([
        StructField('urls', ArrayType(StringType()), False),
        StructField('predictions', ArrayType(StringType()), False),
        StructField('occurances', ArrayType(StringType()), False),
        StructField('confidences', ArrayType(StringType()), False)
    ])


@udf(schema_obj_detection) 
def get_entities(video_url):

    response_predicions = []
    response_confidences = []
    bounded_images = []

    results = {
        "urls":[],
        "predictions":[],
        "occurances":[],
        "confidences":[]
    }

    frame_size, frame_urls = vidToFrames(video_url)
    print("Video Frames have been stored on FTP!")
    
    try:
        #print(frame_urls)
        for image_url in frame_urls:
            response = requests.post(f"http://{node_ip_objd}:{node_port_objd}/", json={"imageUrl":image_url})
            objd = response.json()["data"]
            try:    
                objd_data = objd[0]
                # Read image from URL
                img = io_skimage.imread(image_url)
                
                try:
                    response_predicions.extend(objd_data['object_classified'])
                    response_confidences.extend(objd_data['probability_score'])
                    bounding_flag, bounded_figure = plot_Image_Boundings(objd_data, img, frame_size)
                    if bounding_flag == True:                    
                        array_img, video_size = imageToNumpy(bounded_figure)
                    else:
                        array_img = bounded_figure # already numpy array
                    bounded_images.append(array_img) # Matplot Image Object
                    
                except Exception as E:
                    print(E)
                    
            except Exception as E:
                    print(E)
        
        print("Object Detection has been performend on all Frames!")
        
        emptyFTPDir()  # Removing all Frames of a video

        if not video_size: # didn't get any boundings from the video
            height, width, layers1 = array_img.shape # use this shape/size
            video_size = (width,height)

        ftp_url = videoToFTP(bounded_images, video_size)
        obj_predicitions, obj_occurances, obj_confidences = objClassified(response_predicions,response_confidences)

        results["urls"].append(ftp_url)
        results["predictions"].append(obj_predicitions)
        results["occurances"].append(obj_occurances)
        results["confidences"].append(obj_confidences)
    
    except Exception as E:
        print(E)
        results["urls"].append("")
        results["predictions"].append("")
        results["occurances"].append("")
        results["confidences"].append("")

    return results

def callback(df):

    outputs_def = df.select("*").withColumn("object_detection_video", get_entities("Video_Links"))
    # outputs_def = df.select("CTR", "GTR", "target_type", "target_subtype", "media_c")\
    #                 .withColumn("Object_Detection",get_entities("media_c"))
    print(outputs_def.show(truncate=False))
    print(outputs_def.printSchema())

    df = df.selectExpr("posts.media_c as media_c","_metadata._id as id")\
        .withColumn("Object_Detection",get_entities("media_c"))\
        .select("object_detection","id")
    df.show()

    es_pyspark_handler.save_to_elastic(elastic_index, df, "id")

    return outputs_def

callback(df)
