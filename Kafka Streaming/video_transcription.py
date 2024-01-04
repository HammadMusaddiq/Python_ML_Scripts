import json
import sys
from pyspark.sql import SparkSession
from pyspark.sql import Row
from pyspark.sql.types import StringType, BooleanType, StructType, StructField
from pyspark.sql.functions import udf, lit
from pydub import AudioSegment
from autocorrect import Speller
import configparser
from io import BytesIO
from urllib.request import urlopen
import io
import re
import requests
from ftplib import FTP, error_perm

from OwlsenseStream import OwlsenseStream

stream = OwlsenseStream(read_topic="trimmed-videos", write_topic="video-transcription", feature_name="VIDEO_TRANSCRIPTION")
spark = stream.get_spark_context()

global ftp
ftp = FTP()

conf_path = "hdfs:///user/config/config.ini"


def initialize_config(spark):
    global node_ip_trc
    global node_port_trc
    global node_ip_ftp
    global node_port_ftp
    global auth_user_ftp
    global auth_pass_ftp

    parse_str = configparser.ConfigParser()
    c = spark.sparkContext.textFile(conf_path).collect()
    buf = io.StringIO("\n".join(c))
    x = parse_str.readfp(buf)
    node_ip_trc = str(parse_str.get('TRANSCRIPTION', 'ip'))
    node_port_trc = str(parse_str.get('TRANSCRIPTION', 'port'))
    node_ip_ftp = str(parse_str.get('FTP', 'host'))
    node_port_ftp = str(parse_str.get('FTP', 'port'))
    auth_user_ftp = str(parse_str.get('FTP', 'username'))
    auth_pass_ftp = str(parse_str.get('FTP', 'password'))


initialize_config(spark)
transcription_url = "http://" + str(node_ip_trc) + ":" + str(node_port_trc) + "/"
print(transcription_url)


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


def save_audio_file(audio_file_name, memoryBuff):
    try:
        connect()
        try:
            login()
            print("Logged In:")
            print("---------------------------")
            ftp.cwd("Audio_Transcription/Audios")
            ftp.storbinary("STOR " + audio_file_name, memoryBuff)

        except:
            print("Login Failed or File could not be saved.")

    except:
        print("No Connection.")


def audio_from_video(video_path):
    ftp.cwd("Audio_Transcription")
    ftp.cwd("Audios")
    video_name = (video_path.split("/")[-1]).split(".")[0]
    audio_file_name = video_name + ".wav"
    base_url = "http://" + str(node_ip_ftp) + "/osint_system/media_files/Audio_Transcription/"
    audio_folder = base_url + "Audios/"
    audio_path = audio_folder + audio_file_name
    print(audio_path)
    try:
        sound = AudioSegment.from_file(BytesIO(urlopen(video_path).read()), "mp4")
        sound = sound.set_channels(1)
        sound = sound.set_frame_rate(16000)
        memoryBuff = BytesIO()
        sound.export(memoryBuff, format="wav")
        save_audio_file(audio_file_name, memoryBuff)
        return audio_path
    except Exception as E:
        print('Video either does not exist or does not have any audio. %s', str(E))


def spell_check(text):
    spell = Speller()
    text_new = spell(str(text))
    return text_new



def emptyFTPDir(dirname):
    try:
        connect()
        try:
            login()
            ftp.cwd(dirname)
            try:
                for file in ftp.nlst():
                    try:
                        ftp.delete(file)  # Delete Files
                    except Exception:
                        ftp.rmd(file)  # Delete Folder
                ftp.quit()
            except Exception as E:
                print(E)
        except Exception as E:
            print(E)
    except Exception as E:
        print(E)

schema_added = StructType([
    StructField("transcription", StringType(), False),
    StructField("is_transcription", BooleanType(), False)])
@udf(schema_added)
def transcribe(video_path):
    transcription = ""
    print(type(video_path))

    if video_path is None or video_path == "":
        flag = False
        return Row('transcription', 'is_transcription')(transcription, False)

    else:
        try:
            print("CONNECTING")
            connect()
            login()
            print("here we are")
            print("running ftp.cwd")

            a_path = audio_from_video(video_path)

            response = requests.post(transcription_url, json={"audio": a_path}, timeout=6400)
            text = response.json()["data"]
            transcription = spell_check(text[0])


            return Row('transcription', 'is_transcription')(transcription, True)
        except:
            return Row('transcription', 'is_transcription')(transcription, False)


def callback(df):
    # df = df.withColumn("data_type", lit("video_transcription"))
    print(df.show(truncate=False))
    output_def = df.select("*", transcribe("trimmed_url").alias("output"))
    return_df = output_def.select("kafka_id", "data_type", "trimmed_url","output.is_transcription", "output.transcription", "topic")

    print(return_df.printSchema())
    print(return_df.show(truncate=False))
    return return_df


stream.start(callback=callback)
