from pyspark.sql import Row
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

from OwlsenseStream import OwlsenseStream
import io
import configparser
import datetime
from ftplib import FTP
import subprocess
import logging

#from trimmed_failed_tasks import FailedTasks
import os

logger = logging.getLogger(__name__)
if (logger.hasHandlers()):
    logger.handlers.clear()
logging.basicConfig(filename = "app.log", level = logging.ERROR)


logging.info('Started')
ctime = str(datetime.datetime.now())
logging.info("Time: "+str(ctime))

# Create Temp Dir
if os.path.isdir("TempVideoDir") == False:
    os.mkdir("TempVideoDir")
    os.chmod("TempVideoDir",0o777)


# for triming url_video, we are reading data from Kafka Topic.
stream = OwlsenseStream(read_topic="videos-to-be-downloaded", write_topic='trimmed-videos', feature_name='trimming')
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


# Video Download
def VideoDownload(video_url, video_name):
    output_filename = "TempVideoDir/"+video_name+".mp4"
    # output_filename = '\"{}\"'.format(output_filename)
    cmd = ['yt-dlp',video_url,'--external-downloader','aria2c',"-S","res,ext:mp4:m4a","--recode","mp4",'-o',output_filename]
    
    process = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

    logging.info("Downloading started : {}".format(video_url))
    #process.wait()
    #process = await asyncio.create_subprocess_exec(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

    # Status
    logging.info("Started Downloading: {}, pid={}".format(video_url, process.pid))

    # Wait for the subprocess to finish
    stdout, stderr = process.communicate()
    download_state = True
    # Progress
    if process.returncode == 0:
        stdout = stdout.decode('utf-8').strip().replace('\n',' ')
        logging.info(
            "Done: {}, pid={}, output: {}".format(video_url, process.pid, stdout)
        )
        subprocess.Popen(["chmod", "777",output_filename])
        
        process.wait()
        
        return download_state

    else:
        download_state = False
        stderr = stderr.decode("utf-8").strip().replace('\n','') #converted to string
        if 'Could not send HEAD request ' in stderr:
            logging.error("Wrong Url Error {}, pid={}, output: {}".format(video_url, process.pid, stderr))
        elif 'gaierror' in stderr and 'Could not send HEAD request' not in stderr:
            logging.error("Internet Unavailable {}, pid={}, output: {}".format(video_url, process.pid, stderr))
        elif 'HTTP Error 404: Not Found' in stderr:
            logging.error("URL Unavailable Error {}, pid={}, output: {}".format(video_url, process.pid, stderr))
        else:
            #FailedTasks.save_to_json(video_url, video_name)
            logging.warn(
                "Retrying URL: An Exception Occured: {}, pid={}, output: {}".format(video_url, process.pid, stderr)
            )


# Video Trimming
def videoTrimming(video_path,start_time,end_time,video_name):

    output_file = "TempVideoDir/"+"Trim"+video_name+".mp4"

    cmd = ["ffmpeg",'-i',video_path,'-ss',start_time,'-to',end_time,'-c:v','copy','-c:a','copy',output_file,'-y'] 

    logging.info("Trimming started : {}".format(output_file))
    process = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    process.wait()

    logging.info("Video Trimming Completed...: ")

    return output_file


# Video to FTP
def videoToFTP(video_path, video_name):
    try: 
        connect()
        try: 
            login()
            chdir("Trimmed_videos") # Change Directory
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

    data = ''
    video_name = str(datetime.datetime.now().timestamp()).replace('.','')

    try: 
        video_check = VideoDownload(url,video_name)
        print("Video Downloaded...")
        if video_check == True:
            video_filename = "TempVideoDir/"+video_name+".mp4"
            trim_video_path = videoTrimming(video_filename,start,end,video_name)
            video_ftp_url = videoToFTP(trim_video_path,video_name)

            if video_ftp_url != False:
                
                logging.info("Trimmed Video Saved to FTP...: "+str(video_ftp_url))
                os.remove("TempVideoDir/"+video_name+".mp4")
                os.remove("TempVideoDir/"+"Trim"+video_name+".mp4")
                data = video_ftp_url

            else:
                data = ''
                
        else:
            data = ''
            
    except Exception as E:
        data = ''
        logging.error("something went wrong... Reason: {}".format(E))


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

#spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.7,org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.0 --conf spark.sql.caseSensitive=True --py-files /home/rapidev/Downloads/Hammad/Git_Clone/Development/bds/kafka_streaming/OwlsenseStream.py /home/rapidev/Downloads/Hammad/Git_Clone/Development/bds/kafka_streaming/pipeline/trim_online_video_stream.py
#spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.7,org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.0 --conf spark.sql.caseSensitive=True --py-files /home/hammad/VScodeProjects/Kafka_Streaming/OwlsenseStream.py /home/hammad/VScodeProjects/Kafka_Streaming/trim_online_video_stream.py

# For heap memory out
#spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.7,org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.0 --conf spark.sql.caseSensitive=True --py-files /home/hammad/VScodeProjects/Kafka_Streaming/OwlsenseStream.py --driverMemory=8g /home/hammad/VScodeProjects/Kafka_Streaming/trim_online_video_stream.py


# spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.3.0,org.apache.spark:spark-sql-kafka-0-10_2.11:2.3.0,com.yammer.metrics:metrics-core:2.2.0 --conf spark.sql.caseSensitive=True --py-files /home/hammad/Downloads/es_pyspark_handler.py,/home/hammad/VScodeProjects/Kafka_Streaming/OwlsenseStream.py /home/hammad/VScodeProjects/Kafka_Streaming/trim_online_video_stream.py