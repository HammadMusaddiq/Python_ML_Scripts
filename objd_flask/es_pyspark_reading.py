
import json

# Elastic Search configuration on Development
def initialize_config():
    global node_ip
    global node_port
    global auth_user
    global auth_pass

    node_ip = "192.168.18.155"
    node_port = "9200"
    auth_user = "elastic"
    auth_pass = "uLTpJqxVihdXTIH7vXKO"

def search_col_by_index_fields_and_type(spark, index, gtr, columns="GTR,CTR", array_cols=None):

    initialize_config()

    """
        spark:          Spark session for current job.                                      < Required >
        index:          Name of ES index                                                    < Required >
        gtr:            GTR code of current target                                          < Required >
        columns:        Columns to fetch from elastic search                                < Optional >
        array_cols:     Columns to with data type array to be fetched from elastic search   < Optional >
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

#for reading this file
# spark-submit --packages org.elasticsearch:elasticsearch-hadoop:7.2.0 "/home/hammad/Downloads/objd_flask/Final Code/object_detection_elastic.py"