#!/usr/bin/env python3


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
import argparse
import numpy as np
import logging
from time import sleep
from json import dumps
from kafka import KafkaProducer
from datetime import datetime
import copy

# CURRENT_KAFKA_IP = ''

# producer = KafkaProducer(bootstrap_servers=['10.100.160.100:9092'],
#                          value_serializer=lambda x: 
#                          dumps(x).encode('utf-8'))


logging.basicConfig(
    level=logging.INFO, format="%(levelname)s: PID %(process)d: %(message)s"
)
logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")

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
producer = ''

stime = datetime.now().strftime("%H:%M:%S")
t1 = datetime.strptime(stime, "%H:%M:%S")

ntime = datetime.now().strftime("%H:%M:%S")
t2 = datetime.strptime(ntime, "%H:%M:%S")


def connect_kafka(kafka_ip):
    producer = KafkaProducer(bootstrap_servers=[kafka_ip],
                         value_serializer=lambda x: 
                         dumps(x).encode('utf-8'))
    return producer


def tiler_src_pad_buffer_probe(pad, info, u_data):
    global CURRENT_CAMERA_URL, producer
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
            frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
        except StopIteration:
            break

        num_rects = frame_meta.num_obj_meta

        # n_frame = pyds.get_nvds_buf_surface(hash(gst_buffer), frame_meta.batch_id)
        # frame_image = np.array(n_frame, copy=True, order="C")
        # frame_image = cv2.cvtColor(frame_image, cv2.COLOR_RGBA2BGRA)
        # original_frame = copy(frame_image)

        l_obj = frame_meta.obj_meta_list
        while l_obj is not None:
            try:
                obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)
                detections.append({
                    # 'id': obj_meta.object_id,
                    'datetime': str(datetime.now()),
                    'label': obj_meta.obj_label,
                    'confidence': obj_meta.confidence,
                    'x': obj_meta.rect_params.left,
                    'y': obj_meta.rect_params.top,
                    'w': obj_meta.rect_params.width,
                    'h': obj_meta.rect_params.height
                })
            except StopIteration:
                break

            # logging.info(f"Frame Number: {frame_number} Object Meta: {obj_meta.rect_params}")
            # logging.info(f"{obj_meta.obj_label} {obj_meta.confidence}")

            try:
                l_obj = l_obj.next
            except StopIteration:
                break
        
        # logging.info(f"Frame Number: {frame_meta.frame_num} Number of Objects: {num_rects}")
        ntime = datetime.now().strftime("%H:%M:%S")
        t2 = datetime.strptime(ntime, "%H:%M:%S")
        if (t2.time() > t1.time()) and len(detections) > 0:
            t1 = copy.deepcopy(t2)
            # detect_dict = {'frame_num': frame_meta.frame_num, 'detections': detections}
            detect_dict = {'detections': detections, 'camera_ip': str(CURRENT_CAMERA_URL)}
            producer.send('streamDetections', value=detect_dict)
            sleep(0.01)

        stream_index = "stream{0}".format(frame_meta.pad_index)
        global perf_data
        perf_data.update_fps(stream_index)
        

        try:
            l_frame = l_frame.next
        except StopIteration:
            break

    return Gst.PadProbeReturn.OK


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


def main(args):
    # Check input arguments
    number_sources = len(args)
    global perf_data
    perf_data = PERF_DATA(number_sources)

    # Standard GStreamer initialization
    Gst.init(None)

    # Create gstreamer elements */
    # Create Pipeline element that will form a connection of other elements
    logging.info("Creating Pipeline \n ")
    pipeline = Gst.Pipeline()
    is_live = False

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
        if uri_name.find("rtsp://") == 0:
            is_live = True
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
    if not nvosd:
        sys.stderr.write(" Unable to create nvosd \n")
    nvvidconv_postosd = Gst.ElementFactory.make("nvvideoconvert", "convertor_postosd")
    if not nvvidconv_postosd:
        sys.stderr.write(" Unable to create nvvidconv_postosd \n")

    # Create a caps filter
    caps = Gst.ElementFactory.make("capsfilter", "filter")
    caps.set_property(
        "caps", Gst.Caps.from_string("video/x-raw(memory:NVMM), format=I420")
    )

    # Make the encoder
    if codec == "H264":
        encoder = Gst.ElementFactory.make("nvv4l2h264enc", "encoder")
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
    updsink_port_num = 5400
    sink = Gst.ElementFactory.make("udpsink", "udpsink")
    if not sink:
        sys.stderr.write(" Unable to create udpsink")

    sink.set_property("host", "224.224.255.255")
    sink.set_property("port", updsink_port_num)
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

    # Start streaming
    rtsp_port_num = 8553
    server = GstRtspServer.RTSPServer.new()
    server.props.service = "%d" % rtsp_port_num
    server.attach(None)

    factory = GstRtspServer.RTSPMediaFactory.new()
    factory.set_launch(
        '( udpsrc name=pay0 port=%d buffer-size=524288 caps="application/x-rtp, media=video, clock-rate=90000, encoding-name=(string)%s, payload=96 " )'
        % (updsink_port_num, codec)
    )
    factory.set_shared(True)
    server.get_mount_points().add_factory("/ds-aix-1", factory)

    logging.info(
        f"\n *** DeepStream: Launched RTSP Streaming at rtsp://localhost:{rtsp_port_num}/ds-aix-1 ***\n\n"
    )

    tiler_sink_pad = tiler.get_static_pad("src")
    if not tiler_sink_pad:
        sys.stderr.write(" Unable to get src pad \n")
    else:
        tiler_sink_pad.add_probe(Gst.PadProbeType.BUFFER, tiler_src_pad_buffer_probe, 0)
        GLib.timeout_add(5000, perf_data.perf_print_callback)

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
    global CURRENT_CAMERA_URL
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
        "-g",
        "--gie",
        default="nvinfer",
        help="choose GPU inference engine type nvinfer or nvinferserver , default=nvinfer",
        nargs="+",
        choices=["nvinfer", "nvinferserver"],
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
    # Check input arguments
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()
    global codec
    global bitrate
    global stream_path
    global gie
    gie = args.gie
    codec = args.codec
    bitrate = args.bitrate
    stream_path = args.input
    CURRENT_CAMERA_URL = args.ip
    CURRENT_KAFKA_IP = args.kafka
    return stream_path, CURRENT_KAFKA_IP


if __name__ == "__main__":

    stream_path, CURRENT_KAFKA_IP = parse_args()
    producer = connect_kafka(CURRENT_KAFKA_IP)
    sys.exit(main(stream_path))
