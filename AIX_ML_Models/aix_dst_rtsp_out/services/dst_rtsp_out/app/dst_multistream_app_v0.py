import sys

sys.path.append("../")
import pyds
import math
from ctypes import *
import gi, ast

gi.require_version("Gst", "1.0")
gi.require_version("GstRtspServer", "1.0")
from gi.repository import Gst, GstRtspServer, GLib
from common.FPS import PERF_DATA
from common.ftp_connection import Ftp_Stream
import argparse
import copy
import os
from time import sleep
from json import dumps
from kafka import KafkaProducer
from datetime import datetime, timedelta
import copy
import numpy as np
import cv2
import logging
import uuid
from PIL import Image
import io

logger = logging.getLogger(__name__) 

node_ip_ftp = os.getenv("node_ip_ftp", "")
node_port_ftp = os.getenv("node_port_ftp", "")
node_path_ftp = os.getenv("node_path_ftp", "")
auth_user_ftp = os.getenv("auth_user_ftp", "")
auth_pass_ftp = os.getenv("auth_pass_ftp", "")

perf_data = PERF_DATA(1)
CURRENT_CAMERA_URL = ''
producer = None
CAMERA_THREATS = {}
producer = ''
NAME = ''
LAT = ''
LONG = ''

mutex = GLib.Mutex()
CROP_QUEUE = []
#OBJECT_TRACKING_CACHE = []

# FTP Connection
try:
    ftp_class = Ftp_Stream(node_ip_ftp, node_port_ftp, node_path_ftp, auth_user_ftp, auth_pass_ftp)
    ftp_cursor = ftp_class.getFTP()
    base_url = ftp_class.getBaseURL()
    FTP_dir_path = "/AIX/livestream_crops/"
    ftp_class.change_ftp_present_working_dir(FTP_dir_path)
    print("FTP Connection Established")
except Exception as e:
    print("Failed to establish connection with FTP")


def imageToFTP(path, file_name, image): #store image on FTP
        image_array = Image.fromarray(np.uint8(image))
        image_bytes = io.BytesIO() 
        image_array.save(image_bytes, format="jpeg") 
        image_bytes.seek(0)

        # logger.info('Uploading Image to FTP')
        if not ftp_class.is_connected():
            ftp_class.retry_ftp_connection()
            ftp_class.change_ftp_present_working_dir(path)
        # else:
        #     ftp_class.change_ftp_present_working_dir(path)
        
        try:
            baseurl = base_url # ('str' object has no attribute 'copy')
            # for p in path.split('/'):
            #     baseurl = baseurl + str(p) + '/'
            baseurl = baseurl + path
            ftp_file_url = baseurl + file_name
            ftp_cursor.storbinary("STOR " + file_name , image_bytes)
            # ftp_cursor.quit()
            
            # logger.info("Image saved on Ftp URL: "+str(ftp_file_url))
            return ftp_file_url

        except Exception as E:
            # logger.error("something went wrong... Reason: {}".format(E))
            return False

def send_crop_to_ftp():
    mutex.lock()

    while CROP_QUEUE:
        # Get the next item from the queue and perform some action on it
        item = CROP_QUEUE.pop(0)
        item_frame = item["frame"]
        item_label = item["label"]
        datetime_str = item["datetime_str"]
        try:
            file_name = str(uuid.uuid4())+'.jpeg'
            image_link = imageToFTP(FTP_dir_path, file_name, item_frame)
            # print(f"Image stored to FTP, {image_link}")
            alertDict = {
                "camera_ip": str(CURRENT_CAMERA_URL),
                "crop_image_path": str(image_link),
                "datetime": str(datetime_str),
                "label": str(item_label)
            }
            logging.info("Image Alerts sending to Kafka...")
            producer.send('streamDetectionsImageAlerts', value=alertDict)
        except Exception as e:
            logging.info("FTP ERROR: "+ str(e))

        # print(f"Sending crop of {item.shape} to ftp server")
    
    mutex.unlock()

    return True

def connect_kafka(kafka_ip):
    producer = KafkaProducer(bootstrap_servers=[kafka_ip],
                         value_serializer=lambda x: 
                         dumps(x).encode('utf-8'))
    return producer

def glib_mainloop():
    mainloop = GLib.MainLoop()
    try:
        mainloop.run()
    except KeyboardInterrupt:
        pass
    except BaseException:
        pass

def bus_call(bus, message, pipeline):
    t = message.type
    if t == Gst.MessageType.EOS:
        print("pipeline ended")
        pipeline.set_state(Gst.State.NULL)
        sys.exit()
    elif t == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        print("Error:\n{}\nAdditional debug info:\n{}\n".format(err, debug))
        pipeline.set_state(Gst.State.NULL)
        sys.exit()
    else:
        pass
    return True

def get_sink(mode='display'):
    if mode == 'display':
        return "nveglglessink"
    elif mode == 'fake':
        return 'fakesink'
    elif mode == 'rtsp':
        ## for NVIDIA Encoder
        # return 'nvvideoconvert ! capsfilter caps="video/x-raw(memory:NVMM), format=I420" ! nvv4l2h264enc bitrate=4000000 ! rtph264pay ! udpsink host=224.224.255.255 port={} async=false sync=1 qos=0'.format(SPORT)
        ## for CPU Encoder
        return 'nvvideoconvert ! queue ! capsfilter caps="video/x-raw, format=I420" ! queue ! x264enc bitrate=400000 ! rtph264pay ! udpsink host=224.224.255.255 port={} async=false sync=1 qos=0'.format(SPORT)
    else:
        raise NotImplementedError(f"**{mode}** sink support is currently unavailable")

def get_input_protocol(cam_link=''):
    protocol = cam_link.split("://")[0] 
    if protocol == 'rtsp':
        return f'rtspsrc location={cam_link} ! rtph264depay ! h264parse ! nvv4l2decoder ! nvvideoconvert  ! capsfilter ! queue ! mux.sink_0'
    elif protocol == 'rtmp':
        return f'rtmpsrc location={cam_link} ! flvdemux name=demux  demux.video ! queue ! decodebin ! nvvideoconvert ! queue ! mux.sink_0 demux.audio ! queue ! fakesink'
    else:
        raise NotImplementedError(f"**{cam_link}** have a protocol, which we currently does not support.")

def create_launch_string(camera_link):
    sink = get_sink(mode='rtsp') # rtsp | display | fake
    ip_protocol = get_input_protocol(cam_link=camera_link)
    infer_pipeline = f'nvstreammux name=mux batch-size=1 width=1920 height=1080 ! nvinfer name=pgie config-file-path=/app/configs/config_yolo_6750.txt  \
                      ! nvvideoconvert nvbuf-memory-type=3 ! capsfilter caps="video/x-raw(memory:NVMM), format=RGBA" \
                      ! nvvideoconvert ! nvdsosd name=osd ! {sink} {ip_protocol}'
    #infer_pipeline = f'nvstreammux name=mux batch-size=1 width=1920 height=1080 ! nvinfer name=pgie config-file-path=/app/configs/config_yolo_6750.txt  \
    #                ! nvtracker tracker-width=640 tracker-height=384 gpu-id=0 \
    #                ll-lib-file=/opt/nvidia/deepstream/deepstream/lib/libnvds_nvmultiobjecttracker.so ll-config-file=/app/configs/config_nvDCF_pref.yaml  \
    #                ! nvvideoconvert nvbuf-memory-type=3 ! capsfilter caps="video/x-raw(memory:NVMM), format=RGBA" \
    #                ! nvvideoconvert ! nvdsosd name=osd ! {sink} {ip_protocol}'
    
    return infer_pipeline

def pgie_src_pad_buffer_probe(pad, info, u_data):
    global CURRENT_CAMERA_URL, producer, perf_data, CAMERA_THREATS, NAME, LAT, LONG, IMG_THREATS
   
    gst_buffer = info.get_buffer()
    if not gst_buffer:
        print("Unable to get GstBuffer ")
        return

    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
    l_frame = batch_meta.frame_meta_list
    while l_frame is not None:

        detections = []
        try:
            start_time = datetime.now()
            frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
        except StopIteration:
            break

        l_obj = frame_meta.obj_meta_list
        
        unix_timestamp = frame_meta.ntp_timestamp / 1000000000
        date_string = datetime.fromtimestamp(unix_timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')

        while l_obj is not None:
            try:
                end_time = datetime.now()
                obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)
                if obj_meta.obj_label == 'solider':
                    obj_meta.obj_label = 'soldier'

                detections.append({
                    # 'id': obj_meta.object_id,
                    'inference_time': str(end_time-start_time),
                    'datetime': str(date_string),
                    'class_id': str(obj_meta.class_id),
                    'object_id': str(obj_meta.object_id),
                    'label': obj_meta.obj_label,
                    'confidence': obj_meta.confidence,
                    'x': obj_meta.rect_params.left,
                    'y': obj_meta.rect_params.top,
                    'w': obj_meta.rect_params.width,
                    'h': obj_meta.rect_params.height
                })
            except StopIteration:
                break

            try:
                l_obj = l_obj.next
            except StopIteration:
                break


        if (frame_meta.frame_num % 30 == 0) and len(detections) > 0:
            
            n_frame = pyds.get_nvds_buf_surface(hash(gst_buffer), frame_meta.batch_id)
            frame_image = np.array(n_frame, copy=True, order="C")
            frame_image = cv2.cvtColor(frame_image, cv2.COLOR_RGBA2RGB)
            
            for idx, det in enumerate(detections):
                if det["label"].upper() in IMG_THREATS:
                #and det["object_id"] not in OBJECT_TRACKING_CACHE:
                    # print(f"Image saving...{det['label']}.\n")

                    dx, dy, dw, dh = int(det["x"]), int(det["y"]), int(det["w"]), int(det["h"])
                    crop_img = frame_image[dy:dy+dh, dx:dx+dw]

                    mutex.lock()
                    CROP_QUEUE.append({
                        'frame': crop_img,
                        'datetime_str': str(date_string),
                        'label': det["label"],
                    })
                    #OBJECT_TRACKING_CACHE.append(det["object_id"])
                    mutex.unlock()

            detect_dict = {
                'detections': detections, 
                'camera_ip': str(CURRENT_CAMERA_URL), 
                'threats': CAMERA_THREATS,
                'name':str(NAME), 'lat': str(LAT), 'lng': str(LONG)
                }
            producer.send('streamDetectionsEvents', value=detect_dict)
            # sleep(0.01)

        # stream_index = "stream{0}".format(frame_meta.pad_index)
        # global perf_data
        # perf_data.update_fps(stream_index)

        perf_data.update_fps("stream0")
        try:
            l_frame = l_frame.next
        except StopIteration:
            break

    return Gst.PadProbeReturn.OK

def set_callbacks(pipeline):
    global perf_data

    gvawatermark = pipeline.get_by_name("osd")
    # pad = gvawatermark.get_static_pad("src")
    pad = gvawatermark.get_static_pad("sink")
    pad.add_probe(Gst.PadProbeType.BUFFER, pgie_src_pad_buffer_probe, 0)

    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, pipeline)
    # bus.connect("message", bus_call, loop)

    GLib.timeout_add(1000, send_crop_to_ftp)
    # GLib.timeout_add(1000, lambda: perf_data.perf_print_callback(pipeline))
    GLib.timeout_add(5000, perf_data.perf_print_callback)

def parse_args():
    parser = argparse.ArgumentParser(description="RTSP Output OWL-SENSE ")
    parser.add_argument(
        "-i",
        "--input",
        help="Path to input H264 elementry stream",
        type=str,
        required=True,
        default="rtsp://admin:Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0",
        
    )
    parser.add_argument(
        "-p",
        "--ip",
        help="Camera IP",
        type=str,
        required=True,
        default="192.168.23.199",     
    )
    parser.add_argument(
        "-k",
        "--kafka",
        help="Kafka IP",
        type=str,
        required=True,
        default="",     
    )
    parser.add_argument(
        "-o",
        "--out",
        help="RTSP OUT Port",
        type=int,
        required=True,
        default="",     
    )
    parser.add_argument(
        "-t",
        "--threats",
        help="Threats",
        type=str,
        required=True,
        default="",     
    )
    parser.add_argument(
        "-na",
        "--name",
        help="Name",
        type=str,
        required=True,
        default="",     
    )
    parser.add_argument(
        "-la",
        "--lat",
        help="Latitude",
        type=str,
        required=True,
        default="",     
    )
    parser.add_argument(
        "-lo",
        "--long",
        help="Longitude",
        type=str,
        required=True,
        default="",     
    )
    parser.add_argument(
        "-sp",
        "--sport",
        help="sink_port",
        type=int,
        required=True,
        default="",     
    )
    return parser.parse_args()


if __name__ == '__main__':

    args = parse_args()

    IMG_THREATS = list()
    CAMERA_THREATS = ast.literal_eval(args.threats)

    threats_def = {
        "CIVILIAN_VEHICLE": 1,
        "MILITARY_TANK": 2,
        "SOLDIER": 3,
        "MILITARY_VEHICLE": 4,
        "MILITARY_TRUCK": 5,
        "GUN": 6,
        "PISTOL": 7,
        "PERSON": 8,
    }

    for id, val in threats_def.items():
        if val in [int(th_val) for th_val in CAMERA_THREATS.keys()]:
            if 1 == CAMERA_THREATS[str(val)]:
                IMG_THREATS.append(id)
    
    Gst.init(None)

    # cam_link = "rtmp://matthewc.co.uk/vod/scooter.flv" 
    # cam_link = "rtmp://192.168.25.94:1935/live/stream"
    # cam_link = "rtsp://admin:Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0" 
    # cam_link = "abc://matthewc.co.uk/vod/scooter.flv" 

    cam_link = args.input
    CURRENT_KAFKA_IP = args.kafka
    CURRENT_CAMERA_URL = args.ip
    NAME = args.name
    LAT = args.lat
    LONG = args.long
    SPORT = args.sport

    producer = connect_kafka(CURRENT_KAFKA_IP)

    gst_launch_string = create_launch_string(camera_link=cam_link)
    print(gst_launch_string)
    pipeline = Gst.parse_launch(gst_launch_string)

    # loop = GLib.MainLoop()
    # set_callbacks(pipeline, loop)
    set_callbacks(pipeline)

    # Start streaming
    rtsp_port_num = args.out
    server = GstRtspServer.RTSPServer.new()
    server.props.service = "%d" % rtsp_port_num
    server.attach(None)

    factory = GstRtspServer.RTSPMediaFactory.new()
    factory.set_launch(
        '( udpsrc name=pay0 port=%d buffer-size=524288 caps="application/x-rtp, media=video, clock-rate=90000, encoding-name=(string)%s, payload=96 " )'
        % (SPORT, "H264")
    )
    factory.set_shared(True)
    server.get_mount_points().add_factory("/ds-aix", factory)

    pipeline.set_state(Gst.State.PLAYING)

    # try:
    #     loop.run()
    # except BaseException:
    #     pass
    # # cleanup
    # pipeline.set_state(Gst.State.NULL)

    glib_mainloop()

    print("Exiting")
