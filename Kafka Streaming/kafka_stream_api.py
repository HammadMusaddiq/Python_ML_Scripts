import requests
import json
headers = {
    'x-Requested-By' :'admin',
    'Content-Type' : 'application/json'
}



# data = {
#         "conf":{
#             "spark.jars.packages": "org.apache.spark:spark-streaming-kafka-0-8_2.11:2.3.0,com.yammer.metrics:metrics-core:2.2.0,org.apache.spark:spark-sql-kafka-0-10_2.11:2.3.0"
#         },
#         "file": "hdfs:///user/bds/realtime/streams/operations/video_transcription.py",
#         "pyFiles": [
#         "hdfs:///user/bds/realtime/OwlsenseStream.py"
#         ],
#         "queue": "Spark_Batches",
#         "name": "CRYPTIX_VIDEO_TRANSCRIPTION"
#     }



# Api for scripts having pex files
# data = {"queue":"Spark_Batches",
#         "file":"hdfs:///user/bds/realtime/streams/operations/video_transcription.py",
#         "pyFiles":["hdfs:///user/bds/realtime/OwlsenseStream.py"],
#         "name": "CRYPTIX_VIDEO_TRANSCRIPTION",
#         "conf": {
#             "spark.pyspark.python":"/transcription.pex",
#             "spark.executorEnv.PEX_ROOT":"tmp",
#             "spark.yarn.appMasterEnv.PEX_ROOT": "tmp",
#             "spark.executorEnv.PEX_INHERIT_PATH": "prefer",
#             "spark.yarn.appMasterEnv.PEX_INHERIT_PATH": "prefer",
#             "spark.yarn.appMasterEnv.PYSPARK_GATEWAY_SECRET": "this_secret_key",
#             "spark.jars.packages": "org.apache.spark:spark-streaming-kafka-0-8_2.11:2.3.0,com.yammer.metrics:metrics-core:2.2.0,org.apache.spark:spark-sql-kafka-0-10_2.11:2.3.0"
#         }
#     }


data = json.dumps(data)
request = requests.post(url = 'http://10.100.102.101:8998/batches', headers=headers, data=data, verify=False, auth=('rapidev','hammad'))
print(request.content)