import requests
import json
headers = {
    'x-Requested-By' :'admin',
    'Content-Type' : 'application/json'
}

video_url_ftp = ''
video_start_time = ''
video_end_time = ''

data = {
        "numExecutors":2,
        "executorCores":3,
        "executorMemory":"8g",
        "driverMemory":"4g",
        "args":[video_url_ftp, video_start_time, video_end_time],
        "conf":{
            #"spark.pyspark.python":"/objd.pex",
            "spark.executorEnv.PEX_ROOT":"tmp",
            "spark.yarn.appMasterEnv.PEX_ROOT": "tmp",
            "spark.executorEnv.PEX_INHERIT_PATH": "prefer",     
            "spark.yarn.appMasterEnv.PEX_INHERIT_PATH": "prefer",
            "spark.yarn.appMasterEnv.PYSPARK_GATEWAY_SECRET": "this_secret_key",
            "spark.yarn.executor.memoryOverhead": "15g"
        },
        "file": "hdfs:///user/bds/spark/spark_batch/image_analytics/object_detection.py",
        "pyFiles": [
        "hdfs:///user/bds/elastic_search/es_pyspark_handler.py",
        ],
        "queue": "Spark_Batches",
        "name": "Local_video_upload"
    }


# data = { "queue":"Spark_Batches","file":"hdfs:///user/hammad/object_detection_cluster.py",
#          "conf": {
#              "spark.pyspark.python":"/objd.pex",
#              "spark.executorEnv.PEX_ROOT":"tmp",
#              "spark.yarn.appMasterEnv.PEX_ROOT": "tmp",
#              "spark.executorEnv.PEX_INHERIT_PATH": "prefer",      #pyyaml error on kernal, not on cluster
#              "spark.yarn.appMasterEnv.PEX_INHERIT_PATH": "prefer",
#              "spark.yarn.appMasterEnv.PYSPARK_GATEWAY_SECRET": "this_secret_key",
#              "spark.yarn.executor.memoryOverhead": "15g"

#          },
        #  "driverMemory":"32g", #32g
        #  "executorMemory":"16g", #16g
        #  "executorCores":8, 
        #  "numExecutors":1
        #  }

# data = { "queue":"Spark_Batches","file":"hdfs:///user/Hammad/object_detection_cluster.py",
#          "conf": {
#              "spark.pyspark.python":"/root/OBJD_Final.pex",
#              "spark.yarn.appMasterEnv.PEX_INHERIT_PATH": "prefer",
#              "spark.yarn.appMasterEnv.PYSPARK_GATEWAY_SECRET": "this_secret_key",
#          }
#         }

#/root/OBJD.pex with Detectron2
#/root/OBJD_Final.pex without Detectron2

#ObjectDetection_with_Spark.py
#object_detection_cluster.py

# data = { "queue":"Spark_Batches","file":"hdfs:///user/Hammad/object_detection_cluster.py
#         "conf": {"spark.pyspark.python":"/root/OBJD_Final.pex"}}

data = json.dumps(data)
request = requests.post(url = 'http://192.168.18.182:8999/batches', headers=headers, data=data, verify=False, auth=('rapidev','hammad'))
print(request.content)