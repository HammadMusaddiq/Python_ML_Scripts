from kafka import KafkaProducer, KafkaConsumer
from boxPlot import Plot
import json, logging
from multiprocessing import Process
from threading import Thread
import requests
import cv2
import numpy as np
import base64
from boxPlot import Plot
import os
from datetime import datetime
from dotenv import load_dotenv
import ast

# Logging Intialization
logger = logging.getLogger(__name__)
if logger.hasHandlers():
    logger.handlers.clear()

formatter = logging.Formatter("%(asctime)s | %(name)s |  %(levelname)s | %(message)s")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("pipline.log")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

logger.info("Application Started")


def json_serializer(data):
    return json.dumps(data).encode()


def send_data(topic, data):
    """Function to Send Data in Kafka Topic"""
    producer = KafkaProducer(
        bootstrap_servers=mulhim_kafka,
        value_serializer=json_serializer,
    )
    producer.send(topic, data)


def reconnaissance_apis(ftp_url, recon_detection, recon_fixed, message, start_time):
    if recon_detection:
        params = {"img_url": ftp_url}
        res1 = requests.post(api_route_recon, params=params)

    elif recon_fixed:
        data_type = "satellite"
        params = {"model_type": data_type, "img_url": ftp_url}
        res1 = requests.post(api_route_satelite, params=params)

    print(res1.status_code)
    if res1.status_code == 200:
        res = res1.json()
        print("json Response :: ", res)
        logger.info("Reconnaisssance API Response Successful")
        # print("text Repsonse  :: ", res1.text)
        message["status_code"] = res1.status_code
        message["satellite_image_data"] = res
        message["processed_url"] = ftp_url
        end_time = datetime.now()
        time_taken = str(end_time - start_time)
        message["time_taken"] = time_taken
        send_data(image_output_topic, message)
    else:
        res = message
        res["satellite_metadata"] = {}
        res["status_code"] = res1.status_code
        end_time = datetime.now()
        time_taken = str(end_time - start_time)
        res["time_taken"] = time_taken
        send_data(image_output_topic, res)


def non_satellite(ftp_url, message, start_time, reconnaissance):
    payload = {"image_path": ftp_url}
    res1 = requests.post(api_route_image, data=payload)

    print(res1.status_code)
    if res1.status_code == 200:
        res = res1.json()
        print("json Response :: ", res)
        logger.info("Survalance Response Successful")
        # print("text Repsonse  :: ", res1.text)
        res["status_code"] = res1.status_code
        res["kafka_uuid"] = message.get("kafka_uuid")
        res["reconnaissance"] = reconnaissance
        end_time = datetime.now()
        time_taken = str(end_time - start_time)
        res["time_taken"] = time_taken
        send_data(image_output_topic, res)
    else:
        res = message
        res["status_code"] = res1.status_code
        end_time = datetime.now()
        time_taken = str(end_time - start_time)
        res["time_taken"] = time_taken
        send_data(image_output_topic, res)


def drone_api(ftp_url, message, start_time, drone):
    url = api_route_drone + "?image_url=" + str(ftp_url)
    response = requests.request("POST", url)
    if response.status_code == 200:
        res = json.loads(response.json())
        logger.info("Drone API Response Successful")
        res["status_code"] = response.status_code
        res["kafka_uuid"] = message.get("kafka_uuid")
        res["drone_image"] = drone
        res["processed_url"] = res.get("image_link")
        del res["image_link"]
        # message["processed_url"] = res.get("image_link")
        # message["drone_image_metadata"] = res
        end_time = datetime.now()
        time_taken = str(end_time - start_time)
        res["time_taken"] = time_taken
        print(res)

        send_data(image_output_topic, res)


def prespective_ml_model_image(message, start_time):
    """Function For Local Uploaded Photo"""
    try:
        # import pdb

        # pdb.set_trace()
        # print(message)
        ftp_url = message["base_url"]
        reconnaissance = message["reconnaissance"]
        recon_detection = message["recon_detection"]
        recon_fixed = message["recon_fixed"]
        drone = message["drone_image"]
        try:
            # print("Hitting URL")
            if reconnaissance:  ## Checking if image type is satelite or prespective
                reconnaissance_apis(
                    ftp_url, recon_detection, recon_fixed, message, start_time
                )
            elif drone:
                drone_api(ftp_url, message, start_time, drone)

            else:
                non_satellite(ftp_url, message, start_time, reconnaissance)

        except Exception as e:
            import traceback

            print(traceback.print_exc())
            print("Problem in Image API HIT ::  ", e)
            logger.error(f"Problem in Image API HIT :: {e}")
    except:
        import traceback

        print(traceback.print_exc())
        logger.error(f"{traceback.print_exc()}")


def prespective_ml_model_video(message):
    """Function for local uploaded video"""
    try:
        final_message = {}
        video_url = message.get("base_url", "")
        name = message.get("kafka_uuid", "0")
        drone = message.get("drone_video", False)
        vid = cv2.VideoCapture(video_url, cv2.CAP_FFMPEG)
        fps = vid.get(cv2.CAP_PROP_FPS)
        fps = int(fps)
        print("FPS in uploaded video ::  ", fps)
        logger.info(f"FPS in uploaded video ::  {fps}")
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
                    if drone:
                        res1 = requests.post(api_route_drone_video, files=files)
                    else:
                        res1 = requests.post(api_route_video, files=files)
                    if res1.status_code == 200:
                        if drone:
                            response = json.loads(res1.json())  ## For drone
                            image = response["image_bytes"]  ## For Drone

                        else:
                            response = res1.json()  ## For survellence
                            image = response["processed_url"]  ## For survellence

                        # print(response.keys())
                        ### Image ####
                        image_new = base64.b64decode(image)
                        nparr = np.frombuffer(image_new, dtype=np.uint8)
                        image_trans_3d = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        processed_video_frames.append(image_trans_3d)

                        end_time = datetime.now()

                        if frame_counter % fps == 0:
                            data_dict = {}
                            data_dict["object_count"] = response.get(
                                "object_count", {}
                            )  ### For survilance
                            data_dict["time_in_video"] = second_counter
                            data_dict["confidence"] = response.get("confidence", [])
                            data_dict["bbox"] = response.get("bbox", [])
                            data_dict["label"] = response.get("label", [])
                            ### Calculating time before sending in kafka ###
                            time_taken = str(end_time - start_time)
                            data_dict["time_taken"] = time_taken
                            second_counter += 1
                            metadata.append(data_dict)

                except Exception as e:
                    print("API Video Response Failed :: ", e)
                    logger.error(f"API Video Response Failed :: {e}")
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
            logger.error(f"Exception in FTP :: {e}")

        final_message["status_code"] = res1.status_code
        final_message["processed_url"] = ftp_path
        final_message["video_metadata"] = metadata
        final_message["kafka_uuid"] = name
        print(final_message)
        send_data(video_frame_output_topic, final_message)

    except:
        import traceback

        print(traceback.print_exc())
        logger.error(f"Exception in Local Video Function {traceback.print_exc()}")


# def live_feed_data(message):
# try:
#     list_of_labels = message["label"]
#     if len(list_of_labels) > 0:
#         print("Detected List ::  ", list_of_labels)
#         send_data(plotted_video_url, message)
# except Exception as e:
#     print(e)


def camera_feed_data(message):
    try:
        ip = message["ip"]
        port = message.get("port", 0000)
        name = message.get("name", "")
        username = message.get("username", "")
        password = message.get("password", "")
        kafka_ip = message.get("kafka_ip", "")
        ai_op = message.get("ai_service", "")
        feed_protocol = message.get("protocol", "")
        threats = message.get("threats", {})
        out_port = message.get("out_port", 0000)
        lat = message.get("lat", "")
        lng = message.get("lng", "")
        drone_camera = message.get("is_drone_camera", False)
        res1 = dict()
        try:
            lat = lat[:9]
        except:
            lat = lat

        try:
            lng = lng[:9]
        except:
            lng = lng

        docker_port_ml = message.get("docker_port_ml", 0000)

        # print(message)

        try:
            if ai_op == "object_detection":
                if feed_protocol == "rtsp":
                    camera_url = f"{feed_protocol}://{username}:{password}@{ip}:{str(port)}/cam/realmonitor?channel=1&subtype=0"
                elif feed_protocol == "rtmp" and drone_camera:
                    camera_url = f"{feed_protocol}://{ip}:{str(port)}/live/stream"

                message["camera_feed_url"] = camera_url
                url = f'{camera_feed_api}?camera_url={camera_url}&camera_ip={ip}&kafka_ip={kafka_ip}&out_port={out_port}&threats="{threats}"&name={name}&lat={lat}&lng={lng}&sink_port={docker_port_ml}'
                res1 = requests.post(url)
                if res1.status_code == 200:
                    response = res1.json()
                    print(response)
                    message["stream_url"] = response.get("stream_url", "")
                    message["container_id"] = response.get("container_id", "")

            elif ai_op == "drone_detection":
                if feed_protocol == "rtsp":
                    camera_url = f"{feed_protocol}://{username}:{password}@{ip}:{str(port)}/cam/realmonitor?channel=1&26subtype=0"

                    message["camera_feed_url"] = camera_url

                    payload = {
                        "camera_url": camera_url,
                        "camera_ip": ip,
                        "kafka_ip": kafka_ip,
                    }

                    res1 = requests.post(camera_feed_drone_api, data=payload)
                    if res1.status_code == 200:
                        response = res1.json()
                        print(response)
                        message["stream_url"] = response.get("stream_url", "")
                        message["container_id"] = response.get("container_id", "temp_id")
            else:
                message["container_id"] = ""
                message["stream_url"] = "Conditions not met properly"

            send_data(plotted_video_topic, message)
            logger.info("Stream Started")
        except Exception as e:
            print("Exception in rstp request hit  :: ", e)
            logger.error(f"Exception in Stream :: {e}")
    except Exception as e:
        print("Exception in topic data :: ", e)
        logger.error(f"Exception in Topic data :: {e}")


def delete_camera(message):
    try:
        # print("message in delete camera")
        ip = message["ip"]
        port = message["port"]
        name = message["name"]
        username = message["username"]
        password = message["password"]
        kafka_ip = message["kafka_ip"]
        ai_op = message.get("ai_service", "")
        feed_protocol = message.get("protocol", "")
        threats = message.get("threats", {})
        out_port = message.get("out_port", 0000)
        container_id = message.get("container_id", "")
        # camera_url = f"rtsp://{username}:{password}@{ip}:{str(port)}/cam/realmonitor?channel=1&subtype=0"
        # print(camera_url)
        # payload = {"camera_url": camera_url, "camera_ip": ip, "kafka_ip": kafka_ip}

        try:
            if ai_op == "object_detection":
                camera_url = f"{feed_protocol}://{username}:{password}@{ip}:{str(port)}/cam/realmonitor?channel=1&subtype=0"
                url = f"{camera_del_api}?container_id={container_id}"

                # payload = {
                #     "container_id": container_id,
                #     # "camera_ip": ip,
                #     # "kafka_ip": kafka_ip,
                #     # "threats": threats,
                #     # "out_port": out_port,
                # }
                res1 = requests.post(url)
                if res1.status_code == 200:
                    response = res1.json()
                    print(response)
                    message["status_code"] = response.get("success", 200)
                else:
                    message["status_code"] = str(res1.status_code)

                send_data(camera_del_resp_topic, message)
                logger.info("Camera Deleted")

            elif ai_op == "drone_detection":
                camera_url = f"{feed_protocol}://{username}:{password}@{ip}:{str(port)}/cam/realmonitor?channel=1&26subtype=0"
                payload = {
                    "camera_url": camera_url,
                    "camera_ip": ip,
                    "kafka_ip": kafka_ip,
                }

                res1 = requests.post(drone_camera_del_api, data=payload)
                if res1.status_code == 200:
                    response = res1.json()
                    print(response)
                    message["stream_out"] = response.get("stream_out", "")
                    message["Error"] = response.get("Error", False)

                send_data(camera_del_resp_topic, message)
                logger.info("Camera Deleted")
            else:
                print("Route down")
                logger.error("API DOWN")

        except Exception as e:
            print("Exception in delete camere request hit  :: ", e)
            logger.error(f"Excetion in delete camera request hit :: {e}")

    except Exception as e:
        print("Exception in topic data :: ", e)
        logger.error(f"Exception in topic data :: {e}")


def read_from_topic(topic_name):
    try:
        consumer = KafkaConsumer(
            topic_name,
            group_id=topic_name + "-reader11",
            bootstrap_servers=mulhim_kafka,
            auto_offset_reset="latest",
        )
        print("Waiting For Messages")
        logger.info("Waiting for messages")
        for msg in consumer:
            message = json.loads(msg.value)
            if topic_name == "mulhim-images":
                start_time = datetime.now()
                Thread(
                    target=prespective_ml_model_image, args=(message, start_time)
                ).start()
                # prespective_ml_model_image(
                #     message,start_time
                # )
            elif topic_name == "mulhim-videos":
                Thread(target=prespective_ml_model_video, args=(message,)).start()
                # prespective_ml_model_video(
                #     message,
                # )
            elif topic_name == "mulhim-add-camera":
                Thread(target=camera_feed_data, args=(message,)).start()

            elif topic_name == "delete-camera":
                Thread(target=delete_camera, args=(message,)).start()

            elif topic_name == "mulhim-update-camera":
                ## Deleting Camera ##
                container_id = message.get("container_id", "")
                if container_id != None and container_id != "":
                    t1 = Thread(target=delete_camera, args=(message,))
                    t1.start()
                    t1.join()
                    ## Adding  Camera After waiting for deletion ##
                    Thread(target=camera_feed_data, args=(message,)).start()

            consumer.commit()

    except KeyboardInterrupt as e:
        print("\n\nKilled by User")
        logger.info("Killed By USER")


if __name__ == "__main__":
    # list_of_topics = ["mulhim-images", "mulhim-videos", "mulhim-add-camera"]
    # mulhim_kafka = ["10.100.160.100:9092"]
    # image_output_topic = "mulhim-image-response"
    # video_frame_output_topic = "mulhim-video-response"
    # plotted_video_topic = "plotted-video-url"
    # api_route_image = "http://10.100.160.103:8001/insert"
    # api_route_video = "http://10.100.160.103:8001/video"
    # api_route_satelite = "http://10.100.160.103:8002/get_predictions"
    # camera_feed_api = "http://10.100.160.103:8005/dst_app_starter"

    load_dotenv()

    list_of_topics = ast.literal_eval(os.getenv("list_of_topics"))
    mulhim_kafka = ast.literal_eval(os.getenv("mulhim_kafka"))
    image_output_topic = os.getenv("image_output_topic")
    video_frame_output_topic = os.getenv("video_frame_output_topic")
    plotted_video_topic = os.getenv("plotted_video_topic")
    api_route_drone = os.getenv("api_route_drone")
    api_route_drone_video = os.getenv("api_route_drone_video")
    api_route_image = os.getenv("api_route_image")
    api_route_video = os.getenv("api_route_video")
    api_route_satelite = os.getenv("api_route_satelite")
    camera_feed_api = os.getenv("camera_feed_api")
    camera_feed_drone_api = os.getenv("camera_feed_drone_api")
    api_route_recon = os.getenv("api_route_recon")
    camera_del_api = os.getenv("camera_del_api")
    camera_del_topic = os.getenv("camera_del_topic")
    camera_del_resp_topic = os.getenv("camera_del_resp_topic")
    drone_camera_del_api = os.getenv("drone_camera_del_api")

    processes = dict()
    plot = Plot()
    # read_from_topic(list_of_topics[0])
    for topic in list_of_topics:
        processes[topic] = Process(target=read_from_topic, args=(topic,))
        processes[topic].start()
        print(f"Starting Process for Topic {topic} with PID: {processes[topic].pid}")
        logger.info(
            f"Starting Process for Topic {topic} with PID : {processes[topic].pid}"
        )
