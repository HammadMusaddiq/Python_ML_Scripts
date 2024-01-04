import configparser
import cv2
import requests
from elasticsearch import Elasticsearch
import pyspark.sql.functions as F
from pyspark.sql import SparkSession
import io
import json
from ftplib import FTP
import random
import datetime
from PIL import Image
import numpy as np

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
    # print(filelist)
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
def ftp_connection(img_name, img_array):
    try:
        connect()
        try:
            login()
            chdir("Weapon_Detection")  # Change Directory

            try:
                image_rgb = Image.fromarray(np.uint8(img_array)).convert('RGB')
                image_bytes = io.BytesIO()
                image_rgb.save(image_bytes, format="png")
                image_bytes.seek(0)

                # Store image to FTP Server
                ftp.storbinary("STOR " + img_name, image_bytes)
                ftp.quit()

                image_bytes.close()

                IMG = BASE_URL + img_name
                return str(IMG)

            except Exception as E:
                print(E)

        except Exception as E:
            print(E)

    except Exception as E:
        print(E)


# FTP Image URL
def ftp_image_url(img1):
    # Image Name Based on Current Time and Random number.
    ran_number = random.getrandbits(25)
    time = datetime.datetime.now().today()
    date_time = time.strftime("%d%m%Y_%H%M%S")
    img_name = "Img" + str(date_time) + "_" + str(ran_number) + ".jpeg"
    image = ftp_connection(img_name, img1)
    return image


def get_entities(list_of_pictures):

    if len(list_of_pictures) == 0:
        value = {
            "is_weapon_detected": ["False"],
            "predictions": [],
            "confidence": [],
            "urls": []
        }
        return value

    # Lists of lists for outputs of all images in the list_of_pictures
    main_is_weapon_detected = list()
    main_labels_list = list()
    main_confidence_list = list()
    main_ftp_url = list()
    for pic in list_of_pictures:
        try:
            response = requests.get(pic)
            img = Image.open(io.BytesIO(response.content))
            arr = np.uint8(img)
            arr = cv2.resize(arr, (640, 640), cv2.INTER_AREA)
        except:
            main_is_weapon_detected.append("False")
            main_labels_list.append([])
            main_confidence_list.append([])
            main_ftp_url.append(pic)
            continue

        image_bytes = cv2.imencode('.jpg', arr)[1].tobytes()  # numpy to bytes
        files = {'image_path': image_bytes}
        response = requests.post(weapon_post_url, files=files)  # send image as bytes with request
        labels_list = response.json()["label"]
        confidence_list = response.json()["confidence"]
        bbox_list = response.json()["bbox"]
        image = arr
        if len(labels_list) == 0:
            is_weapon_detected = "False"
            ftp_url = pic
        else:
            is_weapon_detected = "True"
            for i in range(0, len(labels_list)):
                label = labels_list[i]
                confidence = confidence_list[i]
                bbox = bbox_list[i]
                print(label, confidence, bbox)
                x = int(bbox[0])
                y = int(bbox[1])
                w = int(bbox[2])
                h = int(bbox[3])
                label = response.json()["label"][0]
                image = cv2.resize(image, (640, 640), cv2.INTER_AREA)
                cv2.rectangle(image, (x, y), (w, h), (0, 0, 255), 3)
                annotated_image = cv2.putText(image, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 2)
            ftp_url = ftp_image_url(annotated_image)

        main_is_weapon_detected.append(is_weapon_detected)
        main_labels_list.append(labels_list)
        main_confidence_list.append(confidence_list)
        main_ftp_url.append(ftp_url)

    value = {
        "is_weapon_detected": main_is_weapon_detected,
        "predictions": main_labels_list,
        "confidence": main_confidence_list,
        "urls": main_ftp_url
    }

    # Dictionary to JSON Object using dumps() method
    # Return JSON Object
    return value


def callback(x):
    x = x.decode('utf-8')
    es = Elasticsearch(f"http://{esip}:{esport}")
    x = json.loads(x)

    if 'media_c' not in x.keys():
        print(
            "=======================================medic_c not found in the data~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(x.get('kafka_id'))
        return json.dumps(x)
    else:
        x['weapon_detection'] = get_entities(x['media_c'])

    data = x['weapon_detection']
    q = {"script": {"source": "ctx._source.weapon_detection = params.data", "lang": "painless",
                    'params': {"data": data}},
         "query": {"match": {"kafka_id": x['kafka_id']}}}
    try:
        es.update_by_query(body=q, index=x['data_type'])
        es.indices.refresh(index=x['data_type'])
    except Exception as e:
        print("====================CONFLICT WHILE UPDATING THE RECORD===================")

    return json.dumps(x)


topic_name = 'preprocessing_completed'
write_topic = "weapon_detection_processed"
ip = ''
conf_path = "hdfs://{}/user/config/config.ini".format(ip)  # Config Path
checkpoint_location = "/home/ubuntu/Desktop/checkp/weapon_checkp"
print("=====================WEAPON DETECTION STREAM======================")
print("Configuration File Path: ", conf_path)

spark = SparkSession \
    .builder \
    .appName("SSKafka") \
    .getOrCreate()
# ============================= Reading Config =============================
credstr = spark.sparkContext.textFile(conf_path).collect()
buf = io.StringIO("\n".join(credstr))

parser = configparser.ConfigParser()
parser.read_file(buf)
node_ip_ftp = str(parser.get('FTP', 'host')).strip()
node_port_ftp = str(parser.get('FTP', 'port')).strip()
auth_user_ftp = str(parser.get('FTP', 'username')).strip()
auth_pass_ftp = str(parser.get('FTP', 'password')).strip()

# node_ip_wod = str(parser.get('WOD', 'ip')).strip()
# node_port_wod = str(parser.get('WOD', 'port')).strip()

node_ip_wod = "10.100.104.200"
node_port_wod = "5017"

esip = str(parser.get('BDS_ES_PROD', 'ip'))
esport = str(parser.get('BDS_ES_PROD', 'port'))

weapon_post_url = "http://" + str(node_ip_wod) + ":" + str(node_port_wod) + "/insert"
BASE_URL = "http://" + node_ip_ftp + "/osint_system/media_files/Weapon_Detection/"
# BASE_URL = "http://" + node_ip_ftp + "/microcrawler/Weapon_Detection/" ## Bahrain/NRTC

KAFKA_CONSUMER_IP = str(parser.get('KAFKA_BROKERS', 'brokers'))
# ============================= END =============================

# Reading data from the Kafka Topic

dfraw = spark.readStream.format('kafka') \
    .option('kafka.bootstrap.servers', KAFKA_CONSUMER_IP) \
    .option('subscribe', topic_name) \
    .load()

calludf = F.udf(lambda x: callback(x))

df = dfraw.withColumn('value', calludf(dfraw['value'])) \
    .select('value')

ds = df.selectExpr("CAST(value AS STRING)") \
    .writeStream \
    .format('console') \
    .option('truncate', False) \
    .option('numRows', 100000) \
    .start()

dsf = df.selectExpr("CAST (value AS STRING)") \
    .writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_CONSUMER_IP) \
    .option("topic", write_topic) \
    .option("checkpointLocation", checkpoint_location) \
    .start()

spark.streams.awaitAnyTermination()
