import requests
import numpy as np

from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import StructType, StructField, StringType, ArrayType

from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog

import datetime
import io
from skimage import io as io_skimage
from PIL import Image
import configparser
from ftplib import FTP

# For access path, on cluster user this ("hdfs:///user/config/config.ini"). on System user this ("hdfs://192.168.18.182/user/config/config.ini")
conf_path = "hdfs://192.168.18.182/user/config/config.ini"

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

# for local flask test
# node = '127.0.0.1'
# port = '5000'

spark = SparkSession.builder.getOrCreate()

initialize_config(spark)

df = spark.read.format("json").option("inferSchema","true").option("multiline","true").load("/home/hammad/VScodeProjects/Kafka_Screaming/Streamed_Data/new_streamed_data.json")

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
        # print(node_ip_ftp)
        # print(node_port_ftp)
        # print(auth_user_ftp)
        # print(auth_pass_ftp)
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
            #print("logged_in")
            # print("/"+ftp.pwd())
            chdir("Object_Detection") # Change Directory

            try:            
                # Read numpy Image from PIL
                image = Image.fromarray(np.uint8(img1)).convert('RGB')
                # Image to Binary Mode
                temp = io.BytesIO() # This is a file object
                image.save(temp, format="jpeg") # Save the content to temp
                temp.seek(0) # Return the BytesIO's file pointer to the beginning of the file
                # Store image to FTP Server
                ftp.storbinary("STOR " + var_date + ".jpeg", temp)
                ftp.quit()
                IMG =  BASE_URL + var_date + ".jpeg"
                return str(IMG)
            except Exception as E:
                print(E)
                #print("Error in Storing Image")
        except Exception as E:
            print(E)
            #print("FTP Login Failed.")
    except Exception as E:
        print(E)
        #print("FTP no Connection.")
        
# FTP Image URL
def ftp_image_url(img1):
    # Image Name Based on Current Time.
    c_time = datetime.datetime.now().today()
    date_time = c_time.strftime("%d%m%Y-%H%M%S")
    var_date = "Img"+date_time 
    image = ftp_connection(var_date,img1)
    return image

def plot_Image_Boundings(objd_data,img_cvt):
    # import json
    # print(    json.dumps(objd_data,indent=4))
    # converting str list to flost list
    objd_data_predicted_axis = []
    for axis in objd_data['predicted_axis']:
        objd_data_predicted_axis.append([float(val) for val in axis])
    # print(objd_data_predicted_axis)
    # print("GOT AXES")
    v = Visualizer(img_cvt[:, :, ::-1], MetadataCatalog.get(model_cfg['DATASETS']['TRAIN'][0]), scale=1.6)
    #print("VISUAL INSTANCE")
    # for list_box,list_score,list_class in zip(objd_data_predicted_axis,objd_data['probability_score'],objd_data['object_classified']):
    for _box,_score,_class in zip(objd_data_predicted_axis,objd_data['probability_score'],objd_data['object_classified']):
        v.draw_box(_box)
        v.draw_text("{}({}%)".format(str(_class),str(_score)),(_box[:2]))
    v = v.get_output()
    # print("DREW BOX")
    bounded_img =  v.get_image()[:, :, ::-1]
    # print("MADE IMAGE")

    return bounded_img

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
    list_of_urls = [["http://192.168.18.33/osint_system/media_files/ess/st_fb_425/54377b03-4c61-481a-acb2-967dd58926ad.jpg",\
        "http://192.168.18.33/osint_system/media_files/lap.jpg",\
        "http://192.168.18.33/osint_system/media_files/new2.jpeg"]]

    for image_url in [url for urls in list_of_urls for url in urls]:
        #print(image_url)
        # Connection with Flask App
        response = requests.post(f"http://{node_ip_objd}:{node_port_objd}/", json={"imageUrl":image_url})
        objd = response.json()["data"]
        try:    
            objd_data = objd[0]
            # Read image from URL
            img = io_skimage.imread(image_url)
            try:
                #print("converted image to BGR")
                bounded_img = plot_Image_Boundings(objd_data, img)
                #img_cvt = cv2.cvtColor(bounded_img, cv2.COLOR_RGB2BGR)
                #print("ADDED BOUNDED BOX")              
                ftp_url = ftp_image_url(bounded_img)
                #print("ADDED TO FTP")
                results["urls"].append(ftp_url)
                results["predictions"].append(objd_data['object_classified'])
                results["confidences"].append(objd_data['probability_score'])
                # results.append({"FTP_image_URL":ftp_url,"object_classified":objd_data['object_classified'],"probability_score":objd_data['probability_score']})

            except Exception as E:
                print(E)
                #print("Error in fetching data.")

        except Exception as E:
                print("Image URL is Expired: " + image_url)
                results["urls"].append("")
                results["predictions"].append([])
                results["confidences"].append([])
    # print(json.dumps(results,indent=4))
    return results


def callback(df):
    
    outputs_def = df.select("CTR", "GTR", "target_type", "target_subtype", "media_c")\
                    .withColumn("Object_Detection",get_entities("media_c"))
    print(outputs_def.selectExpr("object_detection.*").show(truncate=False))

    #outputs_def.coalesce(1).write.format('json').save('new_data2.json')
    #df2 = outputs_def.toPandas()
    #df2.to_json (r'/home/hammad/VScodeProjects/Kafka_Screaming/Streamed_Data/new_data.json')

    return outputs_def

callback(df)

# all working
# spark-submit --conf spark.pyspark.driver.python=./OBJD_v2.pex --conf spark.pyspark.python=./OBJD_v2.pex  object_detection.py
# spark-submit --conf spark.pyspark.driver.python=./OBJD_v2.pex --conf spark.pyspark.python=./OBJD_v2.pex --conf spark.yarn.appMasterEnv.PEX_INHERIT_PATH=prefer --conf spark.yarn.appMasterEnv.PYSPARK_GATEWAY_SECRET=this_secret_key object_detection.py
# spark-submit --conf spark.pyspark.driver.python=./OBJD_v2.pex --conf spark.pyspark.python=./OBJD_v2.pex --conf spark.executorEnv.PEX_ROOT=./tmp --conf spark.yarn.appMasterEnv.PEX_ROOT=./tmp --conf spark.yarn.appMasterEnv.PEX_INHERIT_PATH=prefer --conf spark.yarn.appMasterEnv.PYSPARK_GATEWAY_SECRET=this_secret_key object_detection.py


# not working this --conf spark.executorEnv.PEX_INHERIT_PATH=prefer      # pyyaml error
# spark-submit --conf spark.pyspark.driver.python=./OBJD_v2.pex --conf spark.pyspark.python=./OBJD_v2.pex --conf spark.executorEnv.PEX_ROOT=./tmp --conf spark.yarn.appMasterEnv.PEX_ROOT=./tmp --conf spark.executorEnv.PEX_INHERIT_PATH=prefer --conf spark.yarn.appMasterEnv.PEX_INHERIT_PATH=prefer --conf spark.yarn.appMasterEnv.PYSPARK_GATEWAY_SECRET=this_secret_key object_detection.py