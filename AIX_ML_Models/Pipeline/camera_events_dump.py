from elasticsearch import Elasticsearch
from kafka import KafkaProducer, KafkaConsumer
from json import dumps
import json
from datetime import datetime, timedelta
from multiprocessing import Process
from dotenv import load_dotenv
import os
import ast
from threading import Thread


class elastic:
    def __init__(self):
        load_dotenv()
        # self.kafka = "10.100.160.100:9092"
        self.kafka = ast.literal_eval(os.getenv("mulhim_kafka"))

        self.exception_topic = os.getenv("camera_exception_topic")
        self.ip = os.getenv("es_ip")
        self.es_con = Elasticsearch(self.ip)
        self.producer = KafkaProducer(
            bootstrap_servers=self.kafka,
            value_serializer=lambda x: dumps(x).encode("utf-8"),
        )

    def json_serializer(self, data):
        return json.dumps(data).encode()

    def send_data(self, topic, data):
        """Function to Send Data in Kafka Topic"""
        producer = KafkaProducer(
            bootstrap_servers=self.kafka,
            value_serializer=self.json_serializer,
        )
        producer.send(topic, data)

    def dump_data(self, index_name, data):
        try:
            self.es_con.index(index=index_name, document=data)
        except Exception as e:
            print("Exception In Sending Data to ES With Exception  :: ", str(e))
            data["ES exception"] = str(e)
            try:
                self.producer.send(self.exception_topic, value=data)
            except Exception as e1:
                print("Exception with kafka and es ::  ", str(e1))

    def create_index(self, index_name, topic):
        try:
            settings = {"number_of_shards": 1, "number_of_replicas": 0}
            if topic == "streamDetectionsEvents" or "streamDetectionsAlerts":
                mappings = {
                    "properties": {
                        # "name": {"type": "text"},
                        # "camera_ip": {"type": "text", "fielddata": True},
                        "Events": {"type": "keyword"},
                        "Position": {"type": "text"},
                        "Confidence": {"type": "text"},
                        "inference_time": {
                            "type": "date",
                            "format": "H:m:s.SSSSSS",
                        },
                        "Time": {
                            "type": "date",
                            "format": "yyyy-MM-dd HH:mm:ss.SSSSSS",
                        },
                        "threats": {"type": "object", "enabled": True},
                        "name": {"type": "text"},
                        "lat": {"type": "text"},
                        "lng": {"type": "text"},
                        # "event_no": {"type": "long"},
                        # "threat_value": {"type": "long"},
                        # "force": {"type": "text"},
                    }
                }
            elif topic == "drone_streamDetections":
                mappings = {
                    "properties": {
                        "Events": {"type": "keyword"},
                        "Position": {"type": "text"},
                        "Confidence": {"type": "text"},
                        "inference_time": {
                            "type": "date",
                            "format": "H:m:s.SSSSSS",
                        },
                        "Time": {
                            "type": "date",
                            "format": "yyyy-MM-dd HH:mm:ss.SSSSSS",
                        },
                        "name": {"type": "text"},
                        "lat": {"type": "text"},
                        "lng": {"type": "text"},
                    }
                }

            elif topic == "streamdetectionsimagealerts":
                mappings = {
                    "properties": {
                        "camera_ip": {"type": "keyword"},
                        "ftp_url": {"type": "text"},
                        "time": {
                            "type": "date",
                            "format": "yyyy-MM-dd HH:mm:ss.SSSSSS",
                        },
                        "label": {"type": "keyword"},
                        "priority_level": {"type": "long"},
                    }
                }                

            # Create the new index with the specified settings and mappings
            self.es_con.indices.create(
                index=index_name, body={"settings": settings, "mappings": mappings}
            )
            # self.es_con.indices.create(index=index_name, body={"settings": settings})
        except Exception as e:
            print("Index Already Exists  :: ", e)
        # Confirm that the index was created
        if self.es_con.indices.exists(index=index_name):
            print(f"Index '{index_name}' was created successfully.")
        else:
            print(f"Failed to create index '{index_name}'.")

    def delete_old_index(self, index_delete_name):
        # Connect to Elasticsearch

        # Calculate the cutoff time for the indices
        if index_delete_name == "streamdetectionsevents_*":
            cutoff_time = datetime.utcnow() - timedelta(days=1, hours=12)
        elif (
            index_delete_name == "streamdetectionsalerts_*"
            or index_delete_name == "drone_streamdetections_*" or index_delete_name == "streamDetectionsImageAlerts_*"
        ):
            cutoff_time = datetime.utcnow() - timedelta(days=30, hours=00)

        # Get a list of all indices
        all_indices = self.es_con.indices.get_alias(index=index_delete_name).keys()

        # Loop through each index and check if it is older than the cutoff time
        for index_name in all_indices:
            index_metadata = self.es_con.indices.get(index=index_name)
            index_creation_time = datetime.fromtimestamp(
                float(index_metadata[index_name]["settings"]["index"]["creation_date"])
                / 1000.0
            )
            if index_creation_time < cutoff_time:
                # The index is old enough and not empty, so delete it
                self.es_con.indices.delete(index=index_name)
                print(f"Deleted index '{index_name}' created at {index_creation_time}.")

    def events_process_and_dump(self, message, messag_es, alert_index_name, index_name):
        if len(message.get("detections", [])) > 0:
            for det in message.get("detections"):
                messag_es["Position"] = str(
                    "x=" + str(det.get("x")) + " " + "y=" + str(det.get("y"))
                )
                messag_es["Events"] = det.get("label")
                messag_es["Confidence"] = det.get("confidence")
                messag_es["Time"] = det.get("datetime")
                date_obj = datetime.strptime(messag_es["Time"], "%Y-%m-%d %H:%M:%S.%f")
                date = str(date_obj.date())
                date_obj1 = datetime.strptime(date, "%Y-%m-%d")
                messag_es["date"] = date_obj1.strftime("%d-%m-%Y")
                # print("Date:", date)
                messag_es["inference_time"] = det.get(
                    "inference_time", "0:00:00.000000"
                )
                event_key = messag_es["Events"]
                event_no = object_type_mapping[event_key.upper()]

                threat_value = messag_es["threats"].get(str(event_no), 0)

                messag_es["event_no"] = event_no
                messag_es["threat_value"] = threat_value
                if event_key.upper() in blue_force:
                    messag_es["force"] = "blue_force"
                elif event_key.upper() in red_force:
                    messag_es["force"] = "red_force"

                try:
                    if threat_value != 0 and ("drone" not in index_name):
                        messag_es["lat"] = message.get("lat", "")
                        messag_es["lng"] = message.get("lng", "")
                        messag_es["name"] = message.get("name", "")

                        elastic_cl.send_data(alert_topic, messag_es)
                        Thread(
                            target=elastic_cl.dump_data,
                            args=(
                                alert_index_name,
                                messag_es,
                            ),
                        ).start()
                except Exception as e:
                    print(
                        "Exception in dumping data in kafka topic or alert index  :: ",
                        e,
                    )
                ### Dumping in ES ###

                Thread(
                    target=elastic_cl.dump_data,
                    args=(index_name, messag_es),
                ).start()
                # if len(message["threats"].keys()) > 0:
                # elastic_cl.dump_data(alert_index_name, messag_es)

    def read_from_topic(self, topic_name, index_date, index_name, alert_index_name):
        try:
            consumer = KafkaConsumer(
                topic_name,
                group_id=topic_name + "-reader09",
                bootstrap_servers=self.kafka,
                auto_offset_reset="latest",
            )
            print("Waiting For Messages")
            # logger.info("Waiting for messages")
            for index, msg in enumerate(consumer):

                message = json.loads(msg.value)
                if topic_name == "streamDetectionsEvents":

                    messag_es = {}
                    print("Notifications Dumped  :::  ", index)
                    message = json.loads(msg.value)
                    messag_es["camera_ip"] = message.get("camera_ip", "")
                    messag_es["threats"] = message.get("threats", {})

                    date = datetime.now().date()
                    if abs((date - index_date).days) == 0:
                        index_date = index_date
                    else:
                        try:
                            # elastic_cl.delete_old_index(index_delete_pattern)
                            index_delete_pattern = "streamdetectionsevents_*"
                            index_delete_pattern1 = "streamdetectionsalerts_*"

                            Thread(
                                target=elastic_cl.delete_old_index,
                                args=(index_delete_pattern,),
                            ).start()
                            Thread(
                                target=elastic_cl.delete_old_index,
                                args=(index_delete_pattern1,),
                            ).start()
                            index_date = datetime.now().date()
                            index_name = (
                                topic_name.lower()
                                + "_"
                                + str(index_date).replace("-", "_")
                            )
                            alert_index_name = (
                                alert_topic.lower()
                                + "_"
                                + str(index_date).replace("-", "_")
                            )
                            elastic_cl.create_index(index_name, topic_name)
                            elastic_cl.create_index(alert_index_name, topic_name)

                            # Process(
                            #     target=elastic_cl.create_index,
                            #     args=(index_name,)
                            # ).start()
                        except Exception as e:
                            print("Problem in deleting old indexes ::  ", e)
                            index_date = datetime.now().date()
                            index_name = (
                                topic_name.lower()
                                + "_"
                                + str(index_date).replace("-", "_")
                            )
                            elastic_cl.create_index(index_name, topic_name)
                            # Process(
                            #     target=elastic_cl.create_index,
                            #     args=(index_name,)
                            # ).start()
                    try:
                        Thread(
                            target=elastic_cl.events_process_and_dump,
                            args=(message, messag_es, alert_index_name, index_name),
                        ).start()

                        consumer.commit()
                    except Exception as e:
                        import traceback

                        traceback.print_exc()
                        print("Problem in Dumping data in es :: ", e)
                        consumer.commit()

                if topic_name == "drone_streamDetections":
                    messag_es = {}
                    print("Notifications Dumped For Drone :::  ", index)
                    message = json.loads(msg.value)
                    messag_es["camera_ip"] = message.get("camera_ip")
                    date = datetime.now().date()
                    if abs((date - index_date).days) == 0:
                        index_date = index_date
                    else:
                        try:
                            index_delete_pattern = "drone_streamdetections_*"
                            # elastic_cl.delete_old_index(index_delete_pattern)
                            Thread(
                                target=elastic_cl.delete_old_index,
                                args=(index_delete_pattern,),
                            ).start()
                            index_date = datetime.now().date()
                            index_name = (
                                topic_name.lower()
                                + "_"
                                + str(index_date).replace("-", "_")
                            )
                            elastic_cl.create_index(index_name, topic_name)
                            # Process(
                            #     target=elastic_cl.create_index,
                            #     args=(index_name,topic_name,)
                            # ).start()
                        except Exception as e:
                            print("Problem in deleting old indexes ::  ", e)
                            index_date = datetime.now().date()
                            index_name = (
                                topic_name.lower()
                                + "_"
                                + str(index_date).replace("-", "_")
                            )
                            elastic_cl.create_index(index_name, topic_name)
                            # Process(
                            #     target=elastic_cl.create_index,
                            #     args=(index_name,topic_name,)
                            # ).start()
                    try:
                        Thread(
                            target=elastic_cl.events_process_and_dump,
                            args=(message, messag_es, alert_index_name, index_name),
                        ).start()

                        consumer.commit()
                        # if len(message.get("detections", [])) > 0:
                        #     for det in message.get("detections"):
                        #         messag_es["Position"] = str(
                        #             "x="
                        #             + str(det.get("x"))
                        #             + " "
                        #             + "y="
                        #             + str(det.get("y"))
                        #         )
                        #         messag_es["Events"] = det.get("label")
                        #         messag_es["Confidence"] = det.get("confidence")
                        #         messag_es["Time"] = det.get("datetime")
                        #         messag_es["inference_time"] = det.get(
                        #             "inference_time", "0:00:00.000000"
                        #         )

                        #         Thread(
                        #             target=elastic_cl.dump_data,
                        #             args=(index_name, messag_es),
                        #         ).start()

                        # consumer.commit()
                    except Exception as e:
                        print("Problem in Dumping data in es :: ", e)
                        consumer.commit()

                if topic_name == "streamDetectionsImageAlerts":
                    messag_es = {}
                    print("Notifications Dumped  :::  ", index)
                    message = json.loads(msg.value)
                    messag_es["camera_ip"] = message.get("camera_ip", "")
                    messag_es["ftp_url"] = message.get("crop_image_path", "")
                    messag_es["time"] = message.get(
                        "datetime", "1990-01-01 00:00:00.000000"
                    )
                    messag_es["label"] = message.get("label", "")
                    messag_es["priority_level"]=message.get("level",1)
                    date = datetime.now().date()
                    if abs((date - index_date).days) == 0:
                        index_date = index_date
                    else:
                        try:
                            index_delete_pattern = "streamDetectionsImageAlerts_*"
                            # elastic_cl.delete_old_index(index_delete_pattern)
                            Thread(
                                target=elastic_cl.delete_old_index,
                                args=(index_delete_pattern,),
                            ).start()
                            index_date = datetime.now().date()
                            index_name = (
                                topic_name.lower()
                                + "_"
                                + str(index_date).replace("-", "_")
                            )
                            elastic_cl.create_index(index_name, topic_name)

                        except Exception as e:
                            print("Problem in deleting old indexes ::  ", e)
                            index_date = datetime.now().date()
                            index_name = (
                                topic_name.lower()
                                + "_"
                                + str(index_date).replace("-", "_")
                            )
                            elastic_cl.create_index(index_name, topic_name)
                    try:
                        Thread(
                            target=elastic_cl.dump_data,
                            args=(index_name, messag_es),
                        ).start()

                        elastic_cl.send_data(ftp_topic, messag_es)
                    except Exception as e:
                        print("Exception in Sending Data to kafka  ::  ", e)

        except KeyboardInterrupt as e:
            print("\n\nKilled by User")
            # logger.info("Killed By USER")


if __name__ == "__main__":
    object_type_mapping = {
        "CIVILIAN_VEHICLE": 1,
        "MILITARY_TANK": 2,
        "SOLDIER": 3,
        "MILITARY_VEHICLE": 4,
        "MILITARY_TRUCK": 5,
        "GUN": 6,
        "PISTOL": 7,
        "PERSON": 8,
    }

    load_dotenv()
    list_of_topics = ast.literal_eval(os.getenv("detections_topics"))
    blue_force = ast.literal_eval(os.getenv("blue_force"))
    red_force = ast.literal_eval(os.getenv("red_force"))
    camera_output_topic_name = os.getenv("camera_output_msg_topic")
    ftp_topic = os.getenv("ftp_topic")
    KAFKA_CONSUMER_IP_PORT = ast.literal_eval(os.getenv("mulhim_kafka"))
    alert_topic = os.getenv("alert_topic")

    index_date = datetime.now().date()
    processes = dict()
    elastic_cl = elastic()

    alert_index_name = alert_topic.lower() + "_" + str(index_date).replace("-", "_")
    elastic_cl.create_index(alert_index_name, alert_topic)  ## Creating starting index

    ########################## Starting Processes For Each Topic ###################

    for topic in list_of_topics:
        index_name = topic.lower() + "_" + str(index_date).replace("-", "_")
        # if topic != "streamDetectionsImageAlerts":
        elastic_cl.create_index(index_name, topic)  ## Creating starting index

        processes[topic] = Process(
            target=elastic_cl.read_from_topic,
            args=(topic, index_date, index_name, alert_index_name),
        )
        processes[topic].start()
        print(f"Starting Process for Topic {topic} with PID: {processes[topic].pid}")
        # logger.info(
        #     f"Starting Process for Topic {topic} with PID : {processes[topic].pid}"
        # )
