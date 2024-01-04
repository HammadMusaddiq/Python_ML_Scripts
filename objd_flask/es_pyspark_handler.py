"""
from pyspark.sql import SQLContext
from pyspark.sql import SparkSession
#Spark Session for the job
spark = SparkSession.builder.config('master','yarn').config('appName','BDS').getOrCreate()
#SQLContext for queries
sqlContext = SQLContext(spark)

"""


import json
import requests
from requests.auth import HTTPBasicAuth
import configparser
import io

conf_path = "hdfs://10.10.103.102/user/config/config.ini"
node_ip = None
node_port = None
auth_user = None
auth_pass = None


def initialize_config(spark):
    global node_ip
    global node_port
    global auth_user
    global auth_pass

    # parse_str = configparser.ConfigParser()
    # c = spark.sparkContext.textFile(conf_path).collect()
    # buf = io.StringIO("\n".join(c))
    # x = parse_str.readfp(buf)
    # node_ip = str(parse_str.get('BDS_ES_PROD', 'IP'))
    # node_port = str(parse_str.get('BDS_ES_PROD', 'PORT'))
    # auth_user = str(parse_str.get('BDS_ES_PROD', 'USER'))
    # auth_pass = str(parse_str.get('BDS_ES_PROD', 'PWD'))

    node_ip = '10.10.103.107'
    node_port = '9200'
    auth_user = 'elastic'
    auth_pass = 'changeme'


# Danial Changes
# Suggested: target_type, field and keyword are dynamic

def search_by_index_fields_and_type(spark, index, target_type, field, keyword):
    initialize_config(spark)
    q = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match_phrase": {
                            "_type": target_type
                        }
                    },
                    {
                        "match_phrase": {
                            field: keyword
                        }
                    }
                ]
            }
        }
    }
    df = spark \
        .read \
        .format("es") \
        .option("es.nodes", node_ip) \
        .option("es.port", node_port) \
        .option("es.net.http.auth.user", auth_user) \
        .option("es.net.http.auth.pass", auth_pass) \
        .option("es.read.metadata", True) \
        .option("es.query", json.dumps(q)) \
        .load("{0}".format(index))
    return df


"""
keyword="5fca2c6397193e7528bd980a"
field="GTR"
index="twitter_profile_response_tms"
target_type="posts"
search_by_index_fields_and_type(sqlContext, index, target_type,field, keyword)
"""


def save_to_elastic(elastic_index=None, df=None, update_by_col=None, spark= None):
    if spark is not None:
        initialize_config(spark)
    """
        ========================================================================
                        Save DataFrame to Elastic Search
        ========================================================================

        This function extracts and flattens the profile_information key in twitter incoming json

        @Params

        elastic_index:  Valid elasticsearch index where the data will be sent                           < Required >
        elastic_type:   Type of elasticsearch index where data will be stored                           < Required >
        df:             Spark DF object which is return from HDFS using read_dataframe(path) method     < Required >
        update_by_col:  Update existing elastic search dataframe by column                              < Optional >

        @retrun
            Status: <Bool>

    """
    print(node_ip)
    print(node_port)
    print(auth_user)
    print(auth_pass)
    if all(v is not None for v in [node_ip, node_port, auth_user, auth_pass, elastic_index, df]):
        try:
            if update_by_col is None:
                df.write \
                    .format("es") \
                    .option("es.nodes", node_ip) \
                    .option("es.port", node_port) \
                    .option("es.net.http.auth.user", auth_user) \
                    .option("es.net.http.auth.pass", auth_pass) \
                    .save("{}/_doc".format(elastic_index), mode="append")
            else:
                df.write \
                    .format("org.elasticsearch.spark.sql") \
                    .option("es.nodes", node_ip) \
                    .option("es.port", node_port) \
                    .option("es.net.http.auth.user", auth_user) \
                    .option("es.net.http.auth.pass", auth_pass) \
                    .option("es.mapping.id", update_by_col) \
                    .option("es.mapping.exclude", update_by_col) \
                    .option("es.write.operation", "update") \
                    .save("{}/_doc".format(elastic_index), mode="append")
            return True
        except Exception as ex:
            print(ex)
            raise Exception(""" There was a problem while saving data to elastic search """)


    else:
        raise Exception(""" 

        There was an error while storing dataframe to elastic search.
        Please validate and verify the arguments below

        @Params

        node_ip:        Ip Address of the elasticsearch Node/Cluster                        < Required >
        node_port:      Port of the elasticsearch Node/Cluster                              < Required >
        auth_user:      Valid username for elasticsearch Authentication                     < Required >
        auth_pass:      Valid password for elasticsearch Authentication                     < Required >
        elastic_index:  Valid elasticsearch index where the data will be sent               < Required >
        elastic_type:   Type of elasticsearch index where data will be stored               < Required >
        df: DataFrame object which is return from HDFS using read_dataframe(path) method    < Required >

    """)


def search_col_by_index_fields_and_type(spark, index, gtr, columns="GTR,CTR", array_cols=None):
    """
        spark:          Spark session for current job.                                      < Required >
        index:          Name of ES index                                                    < Required >
        gtr:            GTR code of current target                                          < Required >
        columns:        Columns to fetch from elastic search                                < Optional >
        array_cols:     Columns to with data type array to be fetched from elastic search   < Optional >

    """
    initialize_config(spark)
    q = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "_type": "_doc"
                        }
                    },
                    {
                        "match": {
                            "GTR": gtr
                        }
                    }
                ]
            }
        }
    }
    if array_cols is None:
        # "iso-8859-1"
        df = spark.read.format("es") \
            .option("es.nodes", node_ip) \
            .option("es.port", node_port) \
            .option("es.net.http.auth.user", auth_user) \
            .option("es.net.http.auth.pass", auth_pass) \
            .option("es.read.metadata", True) \
            .option("encoding", "iso-8859-1") \
            .option("es.read.field.include", columns) \
            .option("es.query", json.dumps(q)) \
            .load("{}/_doc".format(index))
    else:
        df = spark.read.format("es") \
            .option("es.nodes", node_ip) \
            .option("es.port", node_port) \
            .option("es.net.http.auth.user", auth_user) \
            .option("es.net.http.auth.pass", auth_pass) \
            .option("es.read.metadata", True) \
            .option("encoding", "iso-8859-1") \
            .option("es.read.field.as.array.include", array_cols) \
            .option("es.read.field.include", columns) \
            .option("es.query", json.dumps(q)) \
            .load("{}/_doc".format(index))

    return df


def del_prev_records(elastic_index, gtr, query_filters={}):
    """
        elastic_index:  Name of ES index                                                    < Required >
        gtr:            GTR code of current target                                          < Required >
        query_filters:  A dictionary of fields to filter data from                          < Optional >

    """
    q = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "_type": "_doc"
                        }
                    },
                    {
                        "match": {
                            "GTR": gtr
                        }
                    }
                ]
            }
        }
    }
    for key in query_filters:
        q["query"]["bool"]["must"].append({
            "match": {
                key: query_filters[key]
            }
        })

    print(q)
    headers = {"Content-Type": "application/json"}
    url = "http://{ip}:{port}/{index}/_doc/_delete_by_query".format(ip=node_ip, port=node_port, index=elastic_index)
    r = requests.post(
        url=url,
        auth=HTTPBasicAuth(auth_user, auth_pass), data=json.dumps(q), headers=headers)

    print(r, url)
    print(r.text)




def get_active_model(spark=None,model_type="CATEGORIZATION"):
    """
        GET ACTIVE MODEL
    """
    initialize_config(spark)
    query = {
    "query": {
        "bool": {
        "must": [
            {
            "match": {
                "state": True
            }
            },
            {
            
            "match": {
                "type": model_type
            }
            }
        ]
        }
    },
    "size":1
    }
    model_index = "ml_models"

    if spark is None:
        raise Exception("Please provide spark context")
        
    df = spark.read\
            .format("es")\
            .option("es.nodes", node_ip)\
            .option("es.port", node_port)\
            .option("es.net.http.user", auth_user)\
            .option("es.net.http.pass", auth_pass)\
            .option("es.read.field.include","name")\
            .option("es.query", json.dumps(query))\
            .load("{}".format(model_index))
    
    if df.count() < 1:
        return None
    
    return df


def get_default_model(spark=None,model_type="CATEGORIZATION"):
    initialize_config(spark)
    query = {
    "query": {
        "bool": {
        "must": [
            {
            "match": {
                "subtype": "default"
            }
            },
            {
            
            "match": {
                "type": model_type
            }
            }
        ]
        }
    },
    "size":1
    }
    model_index = "ml_models"

    if spark is None:
        raise Exception("Please provide spark context")
        
    df = spark.read\
            .format("es")\
            .option("es.nodes", node_ip)\
            .option("es.port", node_port)\
            .option("es.net.http.user", auth_user)\
            .option("es.net.http.pass", auth_pass)\
            .option("es.read.field.include","name")\
            .option("es.query", json.dumps(query))\
            .load("{}".format(model_index))
    
    if df.count() < 1:
        return None
    
    return df












def search_for_frs(spark,index, platform, columns="GTR,CTR", array_cols=None):
    """
        spark:          Spark session for current job.                                      < Required >
        index:          Name of ES index                                                    < Required >
        gtr:            GTR code of current target                                          < Required >
        columns:        Columns to fetch from elastic search                                < Optional >
        array_cols:     Columns to with data type array to be fetched from elastic search   < Optional >

    """
    initialize_config(spark)
    q = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "target_type": platform
                        }
                    }
                ]
            }
        },
        "size": 10000
    }
    if array_cols is None:
        df = spark.read.format("es") \
            .option("es.nodes", node_ip) \
            .option("es.port", node_port) \
            .option("es.net.http.auth.user", auth_user)\
            .option("es.net.http.auth.pass", auth_pass) \
            .option("es.read.metadata", True) \
            .option("encoding", "iso-8859-1") \
            .option("es.read.field.include", columns) \
            .option("es.query", json.dumps(q)) \
            .load("{}/_doc".format(index))\

    else:
        df = spark.read.format("es") \
            .option("es.nodes", node_ip) \
            .option("es.port", node_port) \
            .option("es.net.http.auth.user", auth_user) \
            .option("es.net.http.auth.pass", auth_pass) \
            .option("es.read.metadata", True) \
            .option("encoding", "iso-8859-1") \
            .option("es.read.field.as.array.include", array_cols) \
            .option("es.read.field.include", columns) \
            .option("es.query", json.dumps(q)) \
            .load("{}/_doc".format(index))\
            # df.printSchema()
    # df.show()
    return df