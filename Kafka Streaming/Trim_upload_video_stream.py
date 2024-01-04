import requests
import numpy as np

from pyspark.sql import Row
from pyspark.sql.functions import flatten, udf
from pyspark.sql.types import StructType, StructField, StringType, BinaryType, ArrayType

from OwlSenseStream_new import OwlsenseStream
import uuid
import sys
import io
import configparser
import datetime
from ftplib import FTP
import subprocess
import logging
from Trim_Failed_Tasks import FailedTasks
import os

logger = logging.getLogger(__name__)
if (logger.hasHandlers()):
    logger.handlers.clear()
logging.basicConfig(filename = "app.log", level = logging.DEBUG)

# system arguments for api (url, start_time, end_time)
# video_url = sys.argv[1]
# trim_start_time = sys.argv[2]
# trim_end_time = sys.argv[3]

# Audio Transcription for the uploaded local video (Videos already be in FTP so no need to downlaod them from MDS)
video_url = 'http://10.100.102.114/osint_system/media_files/Trimmed_videos/1650867024077753.mp4'
trim_start_time = '00:00:20'  # HH:MM:SS
trim_end_time = '00:00:30'


# for triming url_video, we are reading data from Kafka Topic.
stream = OwlsenseStream(read_topic=None, write_topic='trimmed-uploaded-videos', feature_name='trimming')
spark = stream.get_spark_context()

# For access path, on cluster user this ("hdfs:///user/config/config.ini"). on System user this ("hdfs://10.100.102.102/user/config/config.ini") or 10.100.102.101
ip = "10.100.102.102"
conf_path = "hdfs://{}/user/config/config.ini".format(ip)

# configuration for FTP
node_ip_ftp = None
node_port_ftp = None
auth_user_ftp  = None
auth_pass_ftp  = None

def initialize_config(spark):
    global node_ip_ftp 
    global node_port_ftp 
    global auth_user_ftp 
    global auth_pass_ftp 

    parse_str = configparser.ConfigParser()
    c = spark.sparkContext.textFile(conf_path).collect()
    buf = io.StringIO("\n".join(c))
    x = parse_str.readfp(buf)
    node_ip_ftp = str(parse_str.get('FTP', 'host')).strip()
    node_port_ftp = str(parse_str.get('FTP', 'port')).strip()
    auth_user_ftp = str(parse_str.get('FTP', 'username')).strip()
    auth_pass_ftp = str(parse_str.get('FTP', 'password')).strip()

initialize_config(spark)

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


base_url = "http://"+node_ip_ftp+"/osint_system/media_files/Trimmed_videos/"
#print(base_url)



# Video Trimming
def videoTrimming(video_path,start_time,end_time,video_name):

    output_file = "TempVideoDir/"+"Trim"+video_name+".mp4"

    #cmd = ["ffmpeg",'-i',video_path,'-ss',start_time,'-to',end_time,'-c:a','copy',output_file,'-y']
    cmd = ["ffmpeg",'-i',video_path,'-ss',start_time,'-to',end_time,'-c:v','copy','-c:a','copy',output_file,'-y'] 


    # According to the python documentation subprocess.run waits for the process to end
    subprocess.run(cmd)

    # process = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    # process.wait()

    return output_file


# Video to FTP
def videoToFTP(video_path, video_name):
    try: 
        connect()
        try: 
            login()
            chdir("Trimmed_uploaded_videos") # Change Directory
            try:            
                video_ftp_url = get_video_ftp_url(video_name)

                logging.info("Saving {} to FTP ".format(video_path))
                file = open(video_path,'rb')   # "rb" (reading the local file in binary mode)
                ftp.storbinary("STOR " + video_name + ".mp4", file)
                ftp.quit()
                file.close()            
                logging.info("Video URL: "+str(video_ftp_url))
                logging.info("Video saved on Ftp URL: "+str(video_ftp_url))
                logging.info('Finished with success')
                return video_ftp_url

            except Exception as E:
                logging.error("something went wrong... Reason: {}".format(E))
                return False

        except Exception as E:
            logging.error("something went wrong... Reason: {}".format(E))
            return False

    except Exception as E:
        # Internet Disconnected
        logging.error("something went wrong... Reason: {}".format(E))
        return False



# Get Video FTP URL
def get_video_ftp_url(video_name):
    """
    @return String  
    """
    video_ftp_url = base_url + str(video_name)+".mp4"
    return video_ftp_url


# UDF Schema
@udf(returnType = StringType()) 
def get_entities(url,start,end):

    # video Trim
    # video upload to ftp
    # return json

    data = ''
    video_name = str(datetime.datetime.now().timestamp()).replace('.','')

    try: 
        
        #video_filename = "TempVideoDir/"+video_name+".mp4"
        trim_video_path = videoTrimming(video_url,start,end,video_name)
        video_ftp_url = videoToFTP(trim_video_path,video_name)

        if video_ftp_url != False:

            os.remove("TempVideoDir/"+video_name+".mp4")
            os.remove("TempVideoDir/"+"Trim"+video_name+".mp4")
            data = video_ftp_url

        else:
            data = ''

    except:
        data = ''


    return data



def callback(df):
    
    output_def = df.select("id", "topic", "video_url", "start_video", "end_video" ,get_entities("video_url","start_video","end_video").alias("trimmed_url"))
    #print(output_def.select("trimmed_url").show(truncate=False))
    
    # output_def = df.select("id", "video_url", "start_video", "end_video")
    # output_def = output_def.withColumn("trimmed_url",get_entities("video_url","start_video","end_video"))

    #print(output_def.printSchema())

    return_df = output_def.select("id","trimmed_url","topic")
    print(return_df.show(truncate=False))

    return return_df

stream.start(callback=callback)
    
#spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.7,org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.0 --conf spark.sql.caseSensitive=True --py-files /home/rapidev/Downloads/Hammad/Git_Clone/Development/bds/kafka_streaming/OwlsenseStream.py /home/rapidev/Downloads/Hammad/Git_Clone/Development/bds/kafka_streaming/pipeline/facial_stream.py
#spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.7,org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.0 --conf spark.sql.caseSensitive=True --py-files /home/hammad/VScodeProjects/Kafka_Streaming/OwlsenseStream.py /home/hammad/VScodeProjects/Kafka_Streaming/object_detection_stream.py

# For heap memory out
#spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.7,org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.0 --conf spark.sql.caseSensitive=True --py-files /home/hammad/VScodeProjects/Kafka_Streaming/OwlsenseStream.py --driverMemory=8g /home/hammad/VScodeProjects/Kafka_Streaming/object_detection_stream.py


# spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.3.0,org.apache.spark:spark-sql-kafka-0-10_2.11:2.3.0,com.yammer.metrics:metrics-core:2.2.0 --conf spark.sql.caseSensitive=True --py-files /home/hammad/Downloads/es_pyspark_handler.py,/home/hammad/VScodeProjects/Kafka_Streaming/OwlsenseStream.py /home/hammad/VScodeProjects/Kafka_Streaming/trim_upload_video_stream.py