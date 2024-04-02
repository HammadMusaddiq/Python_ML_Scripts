import cv2
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
    when,
)
import pyspark.sql.types as T
import requests
from datetime import datetime
import numpy as np
import base64
import os
from datetime import datetime
import os
from boxPlot import Plot


plot = Plot()


def prespective_ml_model_image(baseurl, reconnaissance, recon_detection, recon_fixed):
    """Function For Local Uploaded Photo"""
    if reconnaissance:
        if recon_detection:
            params = {"img_url": baseurl}
            res1 = requests.post(api_route_recon, params=params)
            return res1.json()
        elif recon_fixed:
            data_type = "satellite"
            params = {"model_type": data_type, "img_url": baseurl}
            res1 = requests.post(api_route_satelite, params=params)
            return res1.json()
    else:
        payload = {"image_path": baseurl}
        res1 = requests.post(api_route_image, data=payload)
        return res1.json()


convertUDF2 = udf(prespective_ml_model_image, T.StringType())


def prespective_ml_model_video(kafka_uuid, base_url):
    """Function for local uploaded video"""
    try:
        final_message = {}
        video_url = base_url
        name = kafka_uuid
        vid = cv2.VideoCapture(video_url, cv2.CAP_FFMPEG)
        fps = vid.get(cv2.CAP_PROP_FPS)
        fps = int(fps)
        print("FPS in uploaded video ::  ", fps)
        # fps_divider = int(fps / frames_per_second_output)
        frame_counter = 0
        second_counter = 0
        processed_video_frames = []
        metadata = []
        while vid.isOpened():
            # if frame_counter % fps_divider == 0:
            res, frame1 = vid.read()
            if res:
                start_time = datetime.now()
                shape_image = frame1.shape
                # cvt_frame = cv2.cvtColor(frame1, cv2.COLOR_RGB2BGR)
                frame1 = cv2.imencode(".jpg", frame1)[1].tobytes()
                files = {"image_path": frame1}
                try:
                    res1 = requests.post(api_route_video, files=files)
                    if res1.status_code == 200:
                        response = res1.json()

                        ### Image ####
                        image = response["processed_url"]
                        image_new = base64.b64decode(image)
                        nparr = np.frombuffer(image_new, dtype=np.uint8)
                        image_trans_3d = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        processed_video_frames.append(image_trans_3d)

                        end_time = datetime.now()

                        if frame_counter % fps == 0:
                            data_dict = {}
                            data_dict["object_count"] = response["object_count"]
                            data_dict["time_in_video"] = second_counter
                            data_dict["confidence"] = response["confidence"]
                            data_dict["bbox"] = response["bbox"]
                            data_dict["label"] = response["label"]
                            ### Calculating time before sending in kafka ###
                            time_taken = str(end_time - start_time)
                            data_dict["time_taken"] = time_taken
                            second_counter += 1
                            metadata.append(data_dict)

                except Exception as e:
                    print("API Video Response Failed :: ", e)
                # print(frame_counter)
                frame_counter += 1

            else:
                break
        try:
            updated_path, local_path = plot.createVideo(
                processed_video_frames, shape_image, fps
            )
            # local_path = (
            #     "/home/hamza/Desktop/myrepo/testrepoDE/mulhim_test_code/" + local_path
            # )
            ftp_path = plot.videoToFTP(name, updated_path)
            os.remove(updated_path)  ## To remove file from local

            os.remove(
                local_path
            )  ## To remove file from local after uploading it to FTP
        except Exception as e:
            ftp_path = ""
            print("Exception in FTP  :: ", e)

        final_message["status_code"] = res1.status_code
        final_message["processed_url"] = ftp_path
        final_message["video_metadata"] = metadata
        final_message["kafka_uuid"] = name
        print(final_message)

        return final_message

    except:
        import traceback

        print(traceback.print_exc())


convertUDF = udf(prespective_ml_model_video, T.StringType())


def camera_feed_data(ip, port, username, password, kafka_ip):
    try:
        response = dict()
        camera_url = f"rtsp://{username}:{password}@{ip}:{str(port)}/cam/realmonitor?channel=1&subtype=0"
        # print(camera_url)
        payload = {"camera_url": camera_url, "camera_ip": ip, "kafka_ip": kafka_ip}

        try:
            res1 = requests.post(camera_feed_api, data=payload)
            if res1.status_code == 200:
                response = res1.json()
                print(response)
                return response["stream_url"]
        except Exception as e:
            print("Exception in rstp request hit  :: ", e)
            response["stream_url"] = str(e)
            return response
    except Exception as e:
        response["stream_url"] = str(e)
        print("Exception in topic data :: ", e)
        return response


convertUDF3 = udf(camera_feed_data, T.StringType())


def delete_camera(ip, port, username, password, kafka_ip):
    try:
        response = dict()
        # print("message in delete camera")
        camera_url = f"rtsp://{username}:{password}@{ip}:{str(port)}/cam/realmonitor?channel=1&subtype=0"
        # print(camera_url)
        payload = {"camera_url": camera_url, "camera_ip": ip, "kafka_ip": kafka_ip}

        try:
            res1 = requests.post(camera_del_api, data=payload)
            if res1.status_code == 200:
                response = res1.json()
                print(response)
                return response

            else:
                response["Error"] = res1.status_code
                print("Route down")
                return response
        except Exception as e:
            response["Error"] = str(e)
            print("Exception in delete camere request hit  :: ", e)
            return response
    except Exception as e:
        response["Error"] = str(e)
        print("Exception in topic data :: ", e)
        return response


convertUDF4 = udf(delete_camera, T.StringType())

topics_for_kafka = (
    "mulhim-images-test,mulhim-videos-test,mulhim-add-camera-test,delete-camera-test"
)

schema_dict = dict()
schema_dict["mulhim-images-test"] = T.StructType(
    [
        T.StructField("kafka_uuid", T.StringType(), True),
        T.StructField("base_url", T.StringType(), True),
        T.StructField("reconnaissance", T.BooleanType(), True),
        T.StructField("recon_detection", T.BooleanType(), True),
        T.StructField("recon_fixed", T.BooleanType(), True),
        T.StructField("image", T.BooleanType(), True),
    ]
)
schema_dict["mulhim-videos-test"] = T.StructType(
    [
        T.StructField("kafka_uuid", T.StringType(), True),
        T.StructField("base_url", T.StringType(), True),
        T.StructField("video", T.BooleanType(), True),
    ]
)
schema_dict["mulhim-add-camera-test"] = T.StructType(
    [
        T.StructField("ip", T.StringType(), True),
        T.StructField("port", T.IntegerType(), True),
        T.StructField("add_camera", T.BooleanType(), True),
        T.StructField("username", T.StringType(), True),
        T.StructField("password", T.StringType(), True),
        T.StructField("kafka_ip", T.StringType(), True),
    ]
)
schema_dict["delete-camera-test"] = T.StructType(
    [
        T.StructField("ip", T.StringType(), True),
        T.StructField("port", T.IntegerType(), True),
        T.StructField("delete_camera", T.BooleanType(), True),
        T.StructField("username", T.StringType(), True),
        T.StructField("password", T.StringType(), True),
        T.StructField("kafka_ip", T.StringType(), True),
    ]
)


def batch_func(df, epochid):
    if "image" in df.columns:
        start_time = datetime.now()
        # print(str(start_time))
        # new_col_name = (
        #     "survelliance"
        #     if df.count() > 0
        #     and "processed_url"
        #     in df.select(
        #         convertUDF2(
        #             col("base_url"),
        #             col("reconnaissance"),
        #             col("recon_detection"),
        #             col("recon_fixed"),
        #         )
        #     ).distinct()
        #     # .rdd.map(lambda x: x[0])
        #     .collect()[0][0]
        #     else "satellite"
        # )

        # print("Before UDF  ::  ", str(datetime.now() - start_time))
        batch_df = df.withColumn(
            "new_col_name",
            convertUDF2(
                col("base_url"),
                col("reconnaissance"),
                col("recon_detection"),
                col("recon_fixed"),
            ),
        )

        # df = df.withColumn(
        #     "TMP",
        #     convertUDF2(
        #         col("base_url"),
        #         col("reconnaissance"),
        #         col("recon_detection"),
        #         col("recon_fixed"),
        #     ),
        # ).persist()
        # new_col_name = (
        #     "survelliance"
        #     if df.count() > 0
        #     and "processed_url" in df.select("TMP").distinct().collect()[0][0]
        #     else "satellite"
        # )
        print("After new UDF  ::  ", str(datetime.now() - start_time))

        # batch_df = df.withColumnRenamed("TMP", new_col_name)
        # print("After UDF :: ", str(datetime.now() - start_time))
        end_time = datetime.now()
        batch_df = batch_df.withColumn("time_taken", lit(str(end_time - start_time)))
        batch_df = batch_df.withColumn(
            "value", to_json(struct([batch_df[x] for x in batch_df.columns]))
        )

        if "value" in batch_df.columns:
            batch_df.selectExpr("CAST(value AS STRING)").write.format("kafka").option(
                "kafka.bootstrap.servers", mulhim_kafka
            ).option("topic", image_output_topic).save()

        print("Proccess Time  :: ", str(datetime.now() - start_time))

    if "video" in df.columns:
        batch_df = df.withColumn(
            "video_repsonse",
            convertUDF(
                col("kafka_uuid"),
                col("base_url"),
            ),
        )
        batch_df = batch_df.withColumn(
            "value", to_json(struct([batch_df[x] for x in batch_df.columns]))
        )
        if "value" in batch_df.columns:
            batch_df.selectExpr("CAST(value AS STRING)").write.format("kafka").option(
                "kafka.bootstrap.servers", mulhim_kafka
            ).option("topic", video_frame_output_topic).save()

    if "add_camera" in df.columns:
        batch_df = df.withColumn(
            "stream_url",
            convertUDF3(
                col("ip"),
                col("port"),
                col("username"),
                col("password"),
                col("kafka_ip"),
            ),
        )
        batch_df = batch_df.withColumn(
            "value", to_json(struct([batch_df[x] for x in batch_df.columns]))
        )
        if "value" in batch_df.columns:
            batch_df.selectExpr("CAST(value AS STRING)").write.format("kafka").option(
                "kafka.bootstrap.servers", mulhim_kafka
            ).option("topic", plotted_video_topic).save()

    if "delete_camera" in df.columns:
        batch_df = df.withColumn(
            "delete_response",
            convertUDF4(
                col("ip"),
                col("port"),
                col("username"),
                col("password"),
                col("kafka_ip"),
            ),
        )
        batch_df = batch_df.withColumn(
            "value", to_json(struct([batch_df[x] for x in batch_df.columns]))
        )
        if "value" in batch_df.columns:
            batch_df.selectExpr("CAST(value AS STRING)").write.format("kafka").option(
                "kafka.bootstrap.servers", mulhim_kafka
            ).option("topic", camera_del_resp_topic).save()


if __name__ == "__main__":
    try:
        topics = [
            "mulhim-images-test",
            "mulhim-videos-test",
            "mulhim-add-camera-test",
            "delete-camera-test",
        ]
        mulhim_kafka = "10.100.160.100:9092"
        image_output_topic = "mulhim-image-response-test"
        video_frame_output_topic = "mulhim-video-response-test"
        plotted_video_topic = "plotted-video-url-test"
        camera_del_resp_topic = "delete-camera-response-test"
        api_route_image = "http://10.100.160.103:8001/insert"
        api_route_video = "http://10.100.160.103:8001/video"
        api_route_satelite = "http://10.100.160.103:8002/get_predictions"
        camera_feed_api = "http://10.100.160.103:8005/dst_app_starter"
        api_route_recon = "http://10.100.160.103:8091/get_predictions"
        camera_del_api = "http://10.100.160.103:8005/dst_app_exit"

        spark = SparkSession.builder.appName("SSKafka").getOrCreate()

        spark.sparkContext.setLogLevel("ERROR")
        spark.sparkContext.addPyFile(
            "/home/{}/Desktop/Repos/aix-data-pipelines/Pipeline/boxPlot.py".format(
                os.environ.get("USER")
            )
        )

        dsraw = (
            spark.readStream.format("kafka")
            .option("kafka.bootstrap.servers", mulhim_kafka)
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

            # if "base_url" in test_df.columns:  ## Checking for specific columns
            #     test_df = test_df.withColumn(
            #         "new_col",
            #         convertUDF2(
            #             col("base_url"),
            #             col("reconnaissance"),
            #             col("recon_detection"),
            #             col("recon_fixed"),
            #         ),
            #     )  ## For udf
            test_df1 = test_df.writeStream.foreachBatch(batch_func).start()

        spark.streams.awaitAnyTermination()

    except Exception as e:
        import traceback

        print(traceback.print_exc())
