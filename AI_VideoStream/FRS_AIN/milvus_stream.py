from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
import requests, json
from pywebhdfs.webhdfs import PyWebHdfsClient
import configparser
import io
import logging
import datetime

logger = logging.getLogger(__name__)
if (logger.hasHandlers()):
    logger.handlers.clear()

formatter = logging.Formatter('%(asctime)s | %(name)s |  %(levelname)s | %(message)s')
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("app.log")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

class Milvus_Stream:
    def __init__(self):
        
        # Parsing Local Config File ../config.ini to get ip & port
        self.parse_str = configparser.ConfigParser()
        self.parse_str.read("../config.ini")

        self.node_ip_ES = None
        self.node_port_ES = None
        self.node_ip_Milvus = None
        self.node_port_Milvus = None

        self.node_ip_ES = str(self.parse_str.get('AIN_ES_DB', 'ip')).strip()
        self.node_port_ES = int(self.parse_str.get('AIN_ES_DB', 'port'))

        self.node_ip_Milvus = str(self.parse_str.get('AIN_Milvus3', 'ip')).strip()
        self.node_port_Milvus = int(self.parse_str.get('AIN_Milvus3', 'port'))
        print(self.node_ip_Milvus,self.node_port_Milvus)

        self.client = None
        self.client = self.connect()
        # self.collection_name = "ai_videostream_sel_v2"
        self.collection_name = "ai_videostream_selected"
        self.collection = self.create_collection()
        
        
    def connect(self):
        return connections.connect(alias="default", host=self.node_ip_Milvus, port=self.node_port_Milvus)


    def create_collection(self):
        
        dim = 128
        prime = FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id = True)
        embeddings = FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim = dim)
        schema = CollectionSchema(fields= [prime,embeddings],description="images embeddings")
        collection = Collection(name = self.collection_name,schema = schema)
        collection.load()

        return collection

    
    def dumpToElasticSearch(self,idx,b_axis,image_link,anno_image_link):
        headers = {"Content-Type":"application/json"}
        current_time = datetime.datetime.now()
        c_time = current_time.strftime("%d/%m/%Y %H:%M:%S")
        data = {"date": c_time, "image_id":idx, "url":image_link, "bbox":b_axis, "annotated_image":anno_image_link}

        try:
            response = requests.post("http://"+str(self.node_ip_ES)+":"+str(self.node_port_ES)+"/"+str(self.collection_name)+"_index"+"/_doc",data=json.dumps(data),headers=headers)
            if response.status_code == 200 or response.status_code == 201:
                return True
            else:
                error = ("An Error Occured while inserting Milvus ID in the ES: {}, {} ").format(response.reason, response.status_code)
                logger.error(error)
                return False

        except Exception as e:
            error = "An Exception Occured while inserting Milvus ID in the ES: {}".format(e)
            logger.error(error)
            return False
    
   
    def insert(self,entities):
        """
            Insert Records Into Milvus DB
        """
        logger.info("Milvus Database Embeddings Insertion Started.")
        try:
            collection = self.create_collection()
            logger.info("Milvus Database Connection is Successful.")

            try:
                idx = collection.insert([[entities]]).primary_keys[0]
                logger.info("Embeddings have been inserted in the milvus database.")
                return idx

            except Exception as E:
                error = "An Exception Occured while inserting data in the Milvus Database: {}".format(E)
                logger.error(error)

        except Exception as E:
            error = "An Exception Occured while connecting to Milvus Database: {}".format(E)
            logger.error(error)

        return False


    def queryToElasticSearch(self,query):
        headers = {
            "Content-Type":"application/json"
        }
        response = requests.get("http://"+str(self.node_ip_ES)+":"+str(self.node_port_ES)+"/"+str(self.collection_name)+"_index"+"/_search",data=json.dumps(query),headers=headers)
        try:
            return True, response.json()
        except Exception as e:
            return False, e


    def fetch_image(self,id):
        query = {
            "query":{
                "match":{
                    "image_id":id
                }
            }
        }
        
        images, exception, date = '', '', ''
        success, response = self.queryToElasticSearch(query)
        if success:
            try:
                images = response['hits']['hits'][0]['_source']['url']
                date = response['hits']['hits'][0]['_source']['date']
                logger.info("Image URL has been fetched from ES.")
                return True, {"date":date,"url":images,"success":success, "exception":exception}
            
            except Exception:
                success = False
                exception = "No Image Found for id {}".format(id)
                logger.error(exception)

        else:
            exception = "An Exception Occured while fetching Image URL from ES: {}".format(response)
            logger.error(exception)

        return False, {"date":date,"url":images,"success":success, "exception":exception}


    def search(self,embeddings):
        logger.info("Milvus Database Searching Started.")
        top = 20 # top most similar embeddings
        distance = "l2"
        search_params = {"metric_type": distance, "params": {"nprobe": 20000}}
        
        try:
            collection = self.create_collection()
            logger.info("Milvus Database Connection is Successful.")
            results = collection.search(data=[embeddings], anns_field="embeddings", param=search_params, limit=top, expr=None)
            logger.info("Milvus Database Searching has been completed.")
            image_list = []
            for raw_result in results:
                for result in raw_result:
                    if result.distance <= 80: # threshold to select similar images
                        check, fetched_image = self.fetch_image(result.id)
                        if check:
                            image_list.append({"id":result.id,"distance":result.distance ,"metric":"l2",**fetched_image})

            logger.info("Milvus Matched_images list has been returned.")
            return image_list

        except Exception as e:
            error = "An Exception Occured while searching embeddings from Milvus Database: {}".format(e)
            logger.error(error)
            return False
    
