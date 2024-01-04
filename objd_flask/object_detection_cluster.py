# import os
# os.environ["PYSPARK_GATEWAY_SECRET"] = "secret"
# os.environ["PYSPARK_PYTHON"] = "/root/OBJD.pex"
from os import truncate
from pyspark.sql.functions import udf

import random
import requests
import numpy as np

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, ArrayType

import matplotlib.patheffects as PathEffects
import matplotlib.pyplot as plt
from matplotlib import patches, text, patheffects

import datetime
import io
from skimage import io as io_skimage
import configparser
from ftplib import FTP
import matplotlib as mpl

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

df = spark.read.json("hdfs:///user/hammad/st_rd_8034.json")
#df = spark.read.json("/home/hammad/Downloads/objd_flask/st_tw_6925.json")
df = df.select('content.posts','target_information.CTR', 'target_information.GTR', 'target_information.target_subtype','target_information.target_type')
df = df.select('CTR','GTR','target_type','target_subtype','posts.media_c')
print(df.printSchema())

BASE_URL = "http://"+node_ip_ftp+"/osint_system/media_files/Object_Detection/"
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


# Image to FTP
def ftp_connection(var_date,img1):
    try: 
        connect()
        try: 
            login()
            chdir("Object_Detection") # Change Directory

            try:            
                temp = io.BytesIO() # This is a file object
                img1.savefig(temp, format="jpeg",bbox_inches='tight',pad_inches = 0) # Save the content to temp
                temp.seek(0) # Return the BytesIO's file pointer to the beginning of the file

                # Store image to FTP Server
                ftp.storbinary("STOR " + var_date + ".jpeg", temp)
                ftp.quit()

                temp.close()

                IMG =  BASE_URL + var_date + ".jpeg"
                return str(IMG)

            except Exception as E:
                print(E)

        except Exception as E:
            print(E)

    except Exception as E:
        print(E)

        
# FTP Image URL
def ftp_image_url(img1):
    # Image Name Based on Current Time.
    c_time = datetime.datetime.now().today()
    # date_time = c_time.strftime("%d%m%Y-%H%M%S")
    var_date = "Img"+str(datetime.datetime.now().timestamp()).replace(".","")
    image = ftp_connection(var_date,img1)
    return image

def plot_Image_Boundings(objd_data,img):
    # converting str list to flost list
    objd_data_predicted_axis = []

    for axis in objd_data['predicted_axis']:
            objd_data_predicted_axis.append([float(val) for val in axis])

    if objd_data_predicted_axis: # If object(s) found in the image
        
        fig = plt.figure(figsize=(14,12),facecolor='Black')
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
        
        ftp_url = ftp_image_url(image)  # fig has image object
        return ftp_url 

    else:  # If no object found in the image, img is numpy array of actual image
        return img

# Object Detection Schema
schema_obj_detection = StructType([
        StructField('urls', ArrayType(StringType()), False),
        StructField('predictions', ArrayType(ArrayType(StringType())), False),
        StructField('confidences', ArrayType(ArrayType(StringType())), False)
    ])


@udf(schema_obj_detection) 
def get_entities(list_of_urls):
    results = {
        "urls":[],
        "predictions":[],
        "confidences":[]
    }

    if list_of_urls == []:      # if media_c is empty
        results["urls"].append("")
        results["predictions"].append([])
        results["confidences"].append([])
        return results

    else:                       # if media_c is not emtpy
        global read_data
        read_data = 'False'
        # print(list_of_urls)
        for image_url in list_of_urls:   # for all platforms including reddit
            # print(image_url)
            if isinstance(image_url, list): # None and empty list [], will be excluded here
                for url in image_url:
                    # print(url)
                    if url != 'default': # another reddit condition
                        response = requests.post(f"http://{node_ip_objd}:{node_port_objd}/", json={"imageUrl":url})
                        objd = response.json()["data"]
                        read_data = 'True'
                        # print(read_data)
                        try:    
                            objd_data = objd[0]

                            # Read image from URL
                            img = io_skimage.imread(url)
                            try:
                                image_output = plot_Image_Boundings(objd_data, img)

                                if isinstance(image_output, str):     # if object plotted on the image then the return value will be the url of ftp in string
                                    results["urls"].append(image_output)    
                                else: # if no object found in the image then image url will be same of input image
                                    results["urls"].append(url)    
                                results["predictions"].append(objd_data['object_classified'])
                                results["confidences"].append(objd_data['probability_score'])
                                #print(results)

                            except Exception as E:
                                print(E)

                        except Exception as E:
                                #print("Image URL is Expired: " + url)
                                results["urls"].append("")
                                results["predictions"].append([])
                                results["confidences"].append([])
                    
        if read_data != 'True':       # if have only None, ['default'], and [] -> in media_c list
            results["urls"].append("")
            results["predictions"].append([])
            results["confidences"].append([])

        return results

def callback(df):
    
    outputs_def = df.select("CTR", "GTR", "target_type", "target_subtype", "media_c")\
                    .withColumn("Object_Detection",get_entities("media_c"))
    print(outputs_def.show())

    return outputs_def

callback(df)
