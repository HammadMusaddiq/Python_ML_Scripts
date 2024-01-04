import requests
import json
headers = {
    'x-Requested-By' :'admin',
    'Content-Type' : 'application/json'
}

#args = [GTR, CTR, target_type, target_subtype]

args = ["st_ln_7946", "1", "linkedin", "profile"]

data = { "queue":"Spark_Batches","file":"hdfs:///user/hammad/object_detection.py",
         "pyFiles":["hdfs:///user/bds/elastic_search/es_pyspark_handler.py"],
         "args":args,
         "conf": {
             "spark.pyspark.python":"/objd.pex",  # here on staging pex only works on slash /
             "spark.executorEnv.PEX_ROOT":"tmp",
             "spark.yarn.appMasterEnv.PEX_ROOT": "tmp",
             "spark.executorEnv.PEX_INHERIT_PATH": "prefer",      #pyyaml error on kernal, not on cluster
             "spark.yarn.appMasterEnv.PEX_INHERIT_PATH": "prefer",
             "spark.yarn.appMasterEnv.PYSPARK_GATEWAY_SECRET": "this_secret_key",
             "spark.yarn.executor.memoryOverhead": "15g"

         },
        #  "driverMemory":"32g", #32g
        #  "executorMemory":"16g", #16g
        #  "executorCores":8, 
        #  "numExecutors":1
        }

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
request = requests.post(url = 'http://10.10.103.101:8998/batches', headers=headers, data=data, verify=False, auth=('rapidev','hammad'))
print(request.content)