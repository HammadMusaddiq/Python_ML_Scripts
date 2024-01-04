from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    from_json,
    explode,
    to_json,
    struct,
    udf,
    lit,
    array,
)
import pyspark.sql.types as T
import re
import requests
import glob


def get_struct_schema(spark, file_name):
    df = spark.read.option("multiline", "true").json(f"{file_name}")
    if "_corrupt_record" not in df.columns:
        dfschema = df.schema.json()
        new_schema = T.StructType.fromJson(json.loads(dfschema))
        return new_schema
    else:
        return None


def drop_unused_col(df):
    df = df.drop("value", "key", "partition", "offset", "timestamp", "timestampType")
    return df


categorization_ip = "10.100.102.123"
categorization_port = "5001"


def hash(text):
    hashtags = re.findall(r"#(\w+)", text)
    return hashtags


convertUDF = udf(lambda z: hash(z), T.StringType())


def mention(text):
    men = re.findall(r"@(\w+)", text)
    return men


convertUDF1 = udf(lambda z: mention(z), T.StringType())


def Categorize(text):
    target_text = [text]
    try:
        response = requests.post(
            f"http://{categorization_ip}:{categorization_port}/",
            json={"text": target_text},
        )
        data = str(response.json())
        print(data)
        return data
    except Exception as e:

        data = ""
        print(type(data))
        return data


convertUDF2 = udf(lambda z: Categorize(z), T.StringType())

import json


def add_kafka(dfo):
    exce = dfo[1]
    ind = dfo[2]
    df = json.loads(dfo[0])
    df["exception"] = str(exce)
    df["index_name"] = str(ind)

    return json.dumps(df)


lambda_udf = udf(lambda x: add_kafka(x))


topics_for_kafka = "reddit-user-posts,reddit-subreddit-posts,facebook-user-posts,facebook-page-posts,\
         facebook-page-community-posts,facebook-group-posts,linkedin-user-posts,linkedin-company-posts,\
         instagram-posts,twitter-posts,twitter-search-api"


def batch_func(df, epochid):
    try:
        index_name = ""

        for topic in topics:
            index_name = topic.replace("-", "_").strip()
            dfdump = df
            dfdump.filter(f"topic='{topic}'").drop("value").write.format(
                "org.elasticsearch.spark.sql"
            ).mode("append").option(
                "checkpointLocation", "/home/hamza/Desktop/checkp/es_chk"
            ).option(
                "es.resource", f"{index_name}/doc"
            ).option(
                "es.nodes", "http://192.168.2.101"
            ).option(
                "es.port", "9200"
            ).save()

    except Exception as e:
        exp = str(e)
        dt0 = df.withColumn("excep", lit(exp))
        dt = dt0.withColumn("index_name", lit(index_name))
        dt1 = dt.withColumn("value", col("value").cast("string"))
        dt2 = dt1.withColumn("value", lambda_udf(array("value", "excep", "index_name")))

        dt2.selectExpr("CAST(value AS STRING)").write.format("kafka").option(
            "kafka.bootstrap.servers", "localhost:9092"
        ).option("topic", "my-stream-2").option(
            "checkpointLocation", "/home/hamza/Desktop/checkp/json_chk"
        ).save()


if __name__ == "__main__":
    try:
        topics = []
        schema_dict = dict()

        spark = (
            SparkSession.builder.master("spark://10.100.102.144:7077")
            .appName("SSKafka")
            .getOrCreate()
        )

        spark.sparkContext.setLogLevel("ERROR")

        for path in glob.glob("/home/hamza/Desktop/Repos/testrepo/*.json"):
            try:
                name = path.split("/")[-1].replace(".json", "")
                file_schema = get_struct_schema(spark, path)
                if file_schema != None:
                    topics.append(name)
                    schema_dict[name] = file_schema
                    print(name)
            except Exception as e:
                print(e)
                pass

        dsraw = (
            spark.readStream.format("kafka")
            .option("kafka.bootstrap.servers", "localhost:9092")
            .option("subscribe", topics_for_kafka)
            .option("startingOffsets", "latest")
            .option("enable.auto.commit", True)
            .load()
        )

        for topic in topics:
            test_df = (
                dsraw.filter(f"topic='{topic}'")
                .alias("raw")
                .withColumn(
                    "data", from_json(col("value").cast("string"), schema_dict[topic])
                )
                .select("data.*", "topic")
            )

            test_df = test_df.withColumn(
                "testudf", convertUDF(col("text_c"))
            )  ## For udf

            test_df = test_df.withColumn(
                "testudf1", convertUDF1(col("text_c"))
            )  ## For udf
            if "text_a" in test_df.columns:  ## Checking for specific columns
                test_df = test_df.withColumn(
                    "testudf2", convertUDF2(col("text_a"))
                )  ## For udf

            test_df = test_df.withColumn(
                "value", to_json(struct([test_df[x] for x in test_df.columns]))
            )  ## from different columns to json

            query = test_df.writeStream.foreachBatch(batch_func).start()

        spark.streams.awaitAnyTermination()

    except Exception as e:
        print(e)
