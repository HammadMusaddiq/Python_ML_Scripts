import requests
import json
headers = {
    'x-Requested-By' :'admin',
    'Content-Type' : 'application/json'
}

# video_url_ftp = ''
# video_start_time = ''
# video_end_time = ''

data = {
        # "numExecutors":2,
        # "executorCores":3,
        # "executorMemory":"8g",
        # "driverMemory":"4g",
        #"args":[video_url_ftp, video_start_time, video_end_time],
        "conf":{
            #"spark.pyspark.python":"/objd.pex",
            #"spark.executorEnv.PEX_ROOT":"tmp",
            #"spark.yarn.appMasterEnv.PEX_ROOT": "tmp",
            #"spark.executorEnv.PEX_INHERIT_PATH": "prefer",     
            #"spark.yarn.appMasterEnv.PEX_INHERIT_PATH": "prefer",
            #"spark.yarn.appMasterEnv.PYSPARK_GATEWAY_SECRET": "this_secret_key",
            #"spark.yarn.executor.memoryOverhead": "15g",
            "spark.jars.packages": "org.apache.spark:spark-streaming-kafka-0-8_2.11:2.3.0,com.yammer.metrics:metrics-core:2.2.0,org.apache.spark:spark-sql-kafka-0-10_2.11:2.3.0"
        },
        #"file": "hdfs:///user/bds/spark/spark_batch/image_analytics/object_detection.py",
        "file": "hdfs:///user/nida/EmoSent.py",
        "pyFiles": [
        #"hdfs:///user/bds/elastic_search/es_pyspark_handler.py",
        "hdfs:///user/bds/realtime/OwlsenseStream.py"
        ],
        "queue": "Spark_Batches",
        "name": "EMO_stream"
    }

data = json.dumps(data)
request = requests.post(url = 'http://10.100.102.101:8998/batches', headers=headers, data=data, verify=False, auth=('rapidev','hammad'))
print(request.content)


# data = { "queue":"Spark_Batches","file":"hdfs:///user/nida/transcription_stream1.py",
#          "pyFiles":["hdfs:///user/bds/realtime/OwlsenseStream.py"],
#          "conf": {
#             "spark.pyspark.python":"/transcription.pex",
#             "spark.executorEnv.PEX_ROOT":"tmp",
#             "spark.yarn.appMasterEnv.PEX_ROOT": "tmp",
#             "spark.executorEnv.PEX_INHERIT_PATH": "prefer",
#             "spark.yarn.appMasterEnv.PEX_INHERIT_PATH": "prefer",
#             "spark.yarn.appMasterEnv.PYSPARK_GATEWAY_SECRET": "this_secret_key",
#             "spark.jars.packages": "org.apache.spark:spark-streaming-kafka-0-8_2.11:2.3.0,com.yammer.metrics:metrics-core:2.2.0,org.apache.spark:spark-sql-kafka-0-10_2.11:2.3.0"
#             }
#          }