import sys

sys.path.append("../")
from common.bus_call import bus_call
from common.is_aarch_64 import is_aarch64
import pyds
import math
from ctypes import *
import gi

gi.require_version("Gst", "1.0")
gi.require_version("GstRtspServer", "1.0")
from gi.repository import Gst, GstRtspServer, GLib

from common.FPS import PERF_DATA
from common.ftp_connection import Ftp_Stream
import argparse
import numpy as np
import logging
from time import sleep
from json import dumps
from kafka import KafkaProducer
from datetime import datetime
import copy, ast, os
from PIL import Image
import io, uuid, cv2

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s: PID %(process)d: %(message)s"
)
logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")

node_ip_ftp = os.getenv("node_ip_ftp", "")
node_port_ftp = os.getenv("node_port_ftp", "")
node_path_ftp = os.getenv("node_path_ftp", "")
auth_user_ftp = os.getenv("auth_user_ftp", "")
auth_pass_ftp = os.getenv("auth_pass_ftp", "")

perf_data = None

MAX_DISPLAY_LEN = 64
MUXER_OUTPUT_WIDTH = 1920
MUXER_OUTPUT_HEIGHT = 1080
MUXER_BATCH_TIMEOUT_USEC = 4000000
TILED_OUTPUT_WIDTH = 1280
TILED_OUTPUT_HEIGHT = 720
GST_CAPS_FEATURES_NVMM = "memory:NVMM"
OSD_PROCESS_MODE = 0
OSD_DISPLAY_TEXT = 0

CURRENT_CAMERA_URL = ''
producer = None
CAMERA_THREATS = {}
producer = ''
NAME = ''
LAT = ''
LONG = ''

mutex = GLib.Mutex()
CROP_QUEUE = []


stime = datetime.now().strftime("%H:%M:%S")
t1 = datetime.strptime(stime, "%H:%M:%S")

ntime = datetime.now().strftime("%H:%M:%S")
t2 = datetime.strptime(ntime, "%H:%M:%S")


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

        if not ftp_class.is_connected():
            ftp_class.retry_ftp_connection()
            ftp_class.change_ftp_present_working_dir(path)
        
        try:
            baseurl = base_url # ('str' object has no attribute 'copy')
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


def tiler_src_pad_buffer_probe(pad, info, u_data):
    global CURRENT_CAMERA_URL, producer, perf_data, CAMERA_THREATS, NAME, LAT, LONG, IMG_THREATS
    global stime, ntime, t1, t2
    
    gst_buffer = info.get_buffer()
    if not gst_buffer:
        logging.info("Unable to get GstBuffer ")
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
        
        # logging.info(f"Frame Number: {frame_meta.frame_num} Number of Objects: {num_rects}")
        ntime = datetime.now().strftime("%H:%M:%S")
        t2 = datetime.strptime(ntime, "%H:%M:%S")
        if (t2.time() > t1.time()) and len(detections) > 0:
            t1 = copy.deepcopy(t2)
            
            n_frame = pyds.get_nvds_buf_surface(hash(gst_buffer), frame_meta.batch_id)
            frame_image = np.array(n_frame, copy=True, order="C")
            frame_image = cv2.cvtColor(frame_image, cv2.COLOR_RGBA2RGB)

            for idx, det in enumerate(detections):
                if det["label"].upper() in IMG_THREATS:
                    # print(f"Image saving...{det['label']}.\n")

                    dx, dy, dw, dh = int(det["x"]), int(det["y"]), int(det["w"]), int(det["h"])
                    crop_img = frame_image[dy:dy+dh, dx:dx+dw]

                    mutex.lock()
                    CROP_QUEUE.append({
                        'frame': crop_img,
                        'datetime_str': str(date_string),
                        'label': det["label"],
                    })
                    mutex.unlock()

            detect_dict = {
                'detections': detections, 
                'camera_ip': str(CURRENT_CAMERA_URL), 
                'threats': CAMERA_THREATS,
                'name':str(NAME), 'lat': str(LAT), 'lng': str(LONG)
                }
            producer.send('streamDetections', value=detect_dict)
            # sleep(0.01)

        stream_index = "stream{0}".format(frame_meta.pad_index)
        global perf_data
        perf_data.update_fps(stream_index)
        

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
    pad.add_probe(Gst.PadProbeType.BUFFER, tiler_src_pad_buffer_probe, 0)

    GLib.timeout_add(1000, send_crop_to_ftp)
    # GLib.timeout_add(1000, lambda: perf_data.perf_print_callback(pipeline))
    GLib.timeout_add(5000, perf_data.perf_print_callback)


def cb_newpad(decodebin, decoder_src_pad, data):
    logging.info("In cb_newpad\n")
    caps = decoder_src_pad.get_current_caps()
    gststruct = caps.get_structure(0)
    gstname = gststruct.get_name()
    source_bin = data
    features = caps.get_features(0)

    logging.info(f"gstname={gstname}")
    if gstname.find("video") != -1:
        logging.info(f"features={features}")
        if features.contains("memory:NVMM"):
            bin_ghost_pad = source_bin.get_static_pad("src")
            if not bin_ghost_pad.set_target(decoder_src_pad):
                sys.stderr.write(
                    "Failed to link decoder src pad to source bin ghost pad\n"
                )
        else:
            sys.stderr.write(" Error: Decodebin did not pick nvidia decoder plugin.\n")


def decodebin_child_added(child_proxy, Object, name, user_data):
    logging.info(f"Decodebin child added: {name}\n")
    if name.find("decodebin") != -1:
        Object.connect("child-added", decodebin_child_added, user_data)


def create_source_bin(index, uri):
    logging.info("Creating source bin")

    bin_name = "source-bin-%02d" % index
    logging.info(bin_name)
    nbin = Gst.Bin.new(bin_name)
    if not nbin:
        sys.stderr.write(" Unable to create source bin \n")

    uri_decode_bin = Gst.ElementFactory.make("uridecodebin", "uri-decode-bin")
    if not uri_decode_bin:
        sys.stderr.write(" Unable to create uri decode bin \n")

    uri_decode_bin.set_property("uri", uri)
    uri_decode_bin.connect("pad-added", cb_newpad, nbin)
    uri_decode_bin.connect("child-added", decodebin_child_added, nbin)

    Gst.Bin.add(nbin, uri_decode_bin)
    bin_pad = nbin.add_pad(Gst.GhostPad.new_no_target("src", Gst.PadDirection.SRC))
    if not bin_pad:
        sys.stderr.write(" Failed to add ghost pad in source bin \n")
        return None
    return nbin


def main(args, codec, bitrate, RTSP_PORT_NUM, SINK_PORT):

    # Check input arguments
    number_sources = len(args) #here args is the camera_url (value is in list)
    global perf_data
    perf_data = PERF_DATA(number_sources)

    # Standard GStreamer initialization
    Gst.init(None)

    # Create Pipeline element that will form a connection of other elements
    logging.info("Creating Pipeline \n ")
    pipeline = Gst.Pipeline()

    if not pipeline:
        sys.stderr.write(" Unable to create Pipeline \n")
    logging.info("Creating streamux \n ")

    # Create nvstreammux instance to form batches from one or more sources.
    streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
    if not streammux:
        sys.stderr.write(" Unable to create NvStreamMux \n")

    pipeline.add(streammux)
    for i in range(number_sources):
        logging.info(f"Creating source_bin {i} \n")
        uri_name = args[i]
        # if uri_name.find("rtsp://") == 0:
        #     is_live = True
        source_bin = create_source_bin(i, uri_name)
        if not source_bin:
            sys.stderr.write("Unable to create source bin \n")
        pipeline.add(source_bin)
        padname = "sink_%u" % i
        sinkpad = streammux.get_request_pad(padname)
        if not sinkpad:
            sys.stderr.write("Unable to create sink pad bin \n")
        srcpad = source_bin.get_static_pad("src")
        if not srcpad:
            sys.stderr.write("Unable to create src pad bin \n")
        srcpad.link(sinkpad)

    logging.info("Creating Pgie \n ")
    pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
    if not pgie:
        sys.stderr.write(" Unable to create pgie \n")

    # logging.info("Creating tgie \n ")
    # tgie = Gst.ElementFactory.make("nvinfer", "secondary-inference")
    # if not tgie:
    #     sys.stderr.write(" Unable to create tgie \n")

    logging.info("Creating tiler \n ")
    tiler = Gst.ElementFactory.make("nvmultistreamtiler", "nvtiler")
    if not tiler:
        sys.stderr.write(" Unable to create tiler \n")
    logging.info("Creating nvvidconv \n ")
    nvvidconv = Gst.ElementFactory.make("nvvideoconvert", "convertor")
    if not nvvidconv:
        sys.stderr.write(" Unable to create nvvidconv \n")
    logging.info("Creating nvosd \n ")
    nvosd = Gst.ElementFactory.make("nvdsosd", "onscreendisplay")
    nvosd.set_property("name", "osd") #added
    if not nvosd:
        sys.stderr.write(" Unable to create nvosd \n")
    nvvidconv_postosd = Gst.ElementFactory.make("nvvideoconvert", "convertor_postosd")
    if not nvvidconv_postosd:
        sys.stderr.write(" Unable to create nvvidconv_postosd \n")

    # Create a caps filter
    caps = Gst.ElementFactory.make("capsfilter", "filter")

    ## Cap (video/x-raw(memory:NVMM) and Codex (nvv4l2h264enc) for to use GPU while encoding
    # caps.set_property(
    #     "caps", Gst.Caps.from_string("video/x-raw(memory:NVMM), format=I420")
    # )
    
    ## Cap (video/x-raw) and Codex (x264enc) for to use CPU while encoding
    caps.set_property(
        "caps", Gst.Caps.from_string("video/x-raw, format=I420")
    )

    # Make the encoder
    if codec == "H264":
        # encoder = Gst.ElementFactory.make("nvv4l2h264enc", "encoder")
        encoder = Gst.ElementFactory.make("x264enc", "encoder")
        logging.info("Creating H264 Encoder")
    elif codec == "H265":
        encoder = Gst.ElementFactory.make("nvv4l2h265enc", "encoder")
        logging.info("Creating H265 Encoder")
    if not encoder:
        sys.stderr.write(" Unable to create encoder")
    encoder.set_property("bitrate", bitrate)
    if is_aarch64():
        encoder.set_property("preset-level", 1)
        encoder.set_property("insert-sps-pps", 1)
        # encoder.set_property("bufapi-version", 1)

    # Make the payload-encode video into RTP packets
    if codec == "H264":
        rtppay = Gst.ElementFactory.make("rtph264pay", "rtppay")
        logging.info("Creating H264 rtppay")
    elif codec == "H265":
        rtppay = Gst.ElementFactory.make("rtph265pay", "rtppay")
        logging.info("Creating H265 rtppay")
    if not rtppay:
        sys.stderr.write(" Unable to create rtppay")

    # Make the UDP sink
    # updsink_port_num = 5400
    sink = Gst.ElementFactory.make("udpsink", "udpsink")
    if not sink:
        sys.stderr.write(" Unable to create udpsink")

    sink.set_property("host", "224.224.255.255")
    sink.set_property("port", SINK_PORT)
    sink.set_property("async", False)
    sink.set_property("sync", 1)

    streammux.set_property("width", 1920)
    streammux.set_property("height", 1080)
    streammux.set_property("batch-size", 1)
    streammux.set_property("batched-push-timeout", 4000000)

    pgie.set_property("config-file-path", f"configs/config_yolo_6750.txt")

    pgie_batch_size = pgie.get_property("batch-size")
    if pgie_batch_size != number_sources:
        logging.info(
            "WARNING: Overriding infer-config batch-size",
            pgie_batch_size,
            " with number of sources ",
            number_sources,
            " \n",
        )
        pgie.set_property("batch-size", number_sources)

    logging.info("Adding elements to Pipeline \n")
    tiler_rows = int(math.sqrt(number_sources))
    tiler_columns = int(math.ceil((1.0 * number_sources) / tiler_rows))
    tiler.set_property("rows", tiler_rows)
    tiler.set_property("columns", tiler_columns)
    tiler.set_property("width", TILED_OUTPUT_WIDTH)
    tiler.set_property("height", TILED_OUTPUT_HEIGHT)
    sink.set_property("qos", 0)

    mem_type = int(pyds.NVBUF_MEM_CUDA_UNIFIED)
    streammux.set_property("nvbuf-memory-type", mem_type)
    nvvidconv.set_property("nvbuf-memory-type", mem_type)
    nvvidconv_postosd.set_property("nvbuf-memory-type", mem_type)
    tiler.set_property("nvbuf-memory-type", mem_type)

    pipeline.add(pgie)
    pipeline.add(tiler)
    pipeline.add(nvvidconv)
    pipeline.add(nvosd)
    pipeline.add(nvvidconv_postosd)
    pipeline.add(caps)
    pipeline.add(encoder)
    pipeline.add(rtppay)
    pipeline.add(sink)

    streammux.link(pgie)
    pgie.link(nvvidconv)
    nvvidconv.link(tiler)
    tiler.link(nvosd)
    nvosd.link(nvvidconv_postosd)
    nvvidconv_postosd.link(caps)
    caps.link(encoder)
    encoder.link(rtppay)
    rtppay.link(sink)

    # create an event loop and feed gstreamer bus mesages to it
    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, loop)

    set_callbacks(tiler)

    server = GstRtspServer.RTSPServer.new()
    server.props.service = "%d" % RTSP_PORT_NUM
    server.attach(None)

    factory = GstRtspServer.RTSPMediaFactory.new()
    factory.set_launch(
        '( udpsrc name=pay0 port=%d buffer-size=524288 caps="application/x-rtp, media=video, clock-rate=90000, encoding-name=(string)%s, payload=96 " )'
        % (SINK_PORT, codec)
    )
    factory.set_shared(True)
    server.get_mount_points().add_factory("/ds-aix-1", factory)

    logging.info(
        f"\n *** DeepStream: Launched RTSP Streaming at rtsp://localhost:{RTSP_PORT_NUM}/ds-aix-1 ***\n\n"
    )

    # start play back and listen to events
    logging.info("Starting pipeline \n")
    pipeline.set_state(Gst.State.PLAYING)
    try:
        loop.run()
    except BaseException:
        pass
    # cleanup
    pipeline.set_state(Gst.State.NULL)


def parse_args():
    parser = argparse.ArgumentParser(description="RTSP Output OWL-SENSE ")
    parser.add_argument(
        "-i",
        "--input",
        help="Path to input H264 elementry stream",
        nargs="+",
        default=["rtsp://admin:Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0"],
    )
    parser.add_argument(
        "-p",
        "--ip",
        help="Camera IP",
        type=str,
        default="192.168.23.199",     
    )
    parser.add_argument(
        "-k",
        "--kafka",
        help="Kafka IP",
        type=str,
        default="",     
    )    
    parser.add_argument(
        "-c",
        "--codec",
        default="H264",
        help="RTSP Streaming Codec H264/H265 , default=H264",
        choices=["H264", "H265"],
    )
    parser.add_argument(
        "-b", "--bitrate", default=4000000, help="Set the encoding bitrate ", type=int
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
        "--sink_port",
        help="sink_port",
        type=int,
        required=True,
        default="",     
    )

    return parser.parse_args()


if __name__ == "__main__":

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

    CURRENT_KAFKA_IP = args.kafka
    CURRENT_CAMERA_URL = args.ip
    NAME = args.name
    LAT = args.lat
    LONG = args.long

    cam_link = args.input
    codec = args.codec
    bitrate = args.bitrate
    sink_port = args.sport
    rtsp_port_num = args.out

    producer = connect_kafka(CURRENT_KAFKA_IP)

    sys.exit(main(cam_link, codec, bitrate, rtsp_port_num, sink_port))

