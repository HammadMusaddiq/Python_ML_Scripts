from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
from flask import Flask
from flask import request
from flask_api import status
import traceback
import logging
from pywebhdfs.webhdfs import PyWebHdfsClient
import configparser
import io

## Logs ##
logger = logging.getLogger(__name__)
if (logger.hasHandlers()):
    logger.handlers.clear()
logging.basicConfig(filename="app.log", level=logging.DEBUG, format="%(asctime)s :: %(levelname)s :: %(message)s")

local_config_parses = configparser.ConfigParser()
local_config_parses.read("./config.ini")
host_hdfs = str(local_config_parses.get('HDFS', 'ip')).strip()
port_hdfs = str(local_config_parses.get('HDFS', 'port'))
hdfs = PyWebHdfsClient(host=host_hdfs,port=port_hdfs, user_name='hdfs')

# Remote config.ini file path located on HDFS
conf_file = '/user/config/config.ini'

node_ip_ftp = None

# Remote HDFS config.ini parser
parse_str = configparser.ConfigParser()

# Reading in Bytes, decode to String
conf_read = hdfs.read_file(conf_file).decode("utf-8") 
buf = io.StringIO(conf_read)
parse_str.readfp(buf)
kafka_broker = str(parse_str.get('KAFKA_BROKERS', 'brokers')).strip()


## Defining Kafka Producer
producer = KafkaProducer(bootstrap_servers=[kafka_broker],value_serializer=lambda m: json.dumps(m).encode('ascii'))

## Initialzing Flask Object
app = Flask('video_information')

## Stating VideoRoute
@app.route("/transcribe",methods=['POST','GET'])
def video_from_url():
    start=request.args.get('start')
    end=request.args.get('end')
    url=request.args.get('url')
    unique_id=request.args.get('id')
    data=    {   
        'kafka_id': unique_id,
        'start_video': start,
        'end_video': end,
        'video_url':url,
        'data_type':'video_transcription'
    }
    try:
        ### Sending Data To Kafka Topic ###
        producer.send('videos-to-be-downloaded', data)
        resp={'Status_code':status.HTTP_200_OK}
        logging.info(f"Data Sent To Topic")

    except Exception as e:
        resp={'Status_code':status.HTTP_400_BAD_REQUEST}
        logging.info("Data Didn't Sent To Topic with error ::  {}".format(e))
        traceback.print_exc()
    return resp


## Starting AudioRoute
@app.route("/audioTranscription",methods=['POST','GET'])
def mp3_from_url():
    url=request.args.get('url')
    unique_id=request.args.get('id')
    data=    {   
        'kafka_id': unique_id,
        'audio_url':url,
        'data_type':'audio_transcription'
    }
    try:
        ### Sending Data To Kafka Topic ###
        producer.send('mp3-to-be-transcribed', data)
        resp={'Status_code':status.HTTP_200_OK}
        logging.info(f"Data Sent To Topic")

    except Exception as e:
        resp={'Status_code':status.HTTP_400_BAD_REQUEST}
        logging.info("Data Didn't Sent To Topic with error ::  {}".format(e))
        traceback.print_exc()
    return resp

# Starting Server
if __name__ == "__main__":
    app.run(debug=True)    


