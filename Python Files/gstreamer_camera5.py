
# import sys
# sys.path.append("../")
# # from common.bus_call import bus_call
# # from common.is_aarch_64 import is_aarch64
# import pyds
# import platform
# import math
# import time
# from ctypes import *
# import gi
# gi.require_version("Gst", "1.0")
# gi.require_version("GstRtspServer", "1.0")
# from gi.repository import Gst, GstRtspServer, GLib
# import configparser

# import argparse

# MAX_DISPLAY_LEN = 64
# MUXER_OUTPUT_WIDTH = 1920
# MUXER_OUTPUT_HEIGHT = 1080
# MUXER_BATCH_TIMEOUT_USEC = 4000000
# TILED_OUTPUT_WIDTH = 1280
# TILED_OUTPUT_HEIGHT = 720
# GST_CAPS_FEATURES_NVMM = "memory:NVMM"
# OSD_PROCESS_MODE = 0
# OSD_DISPLAY_TEXT = 0

# # tiler_sink_pad_buffer_probe  will extract metadata received on OSD sink pad
# # and update params for drawing rectangle, object information etc.


# def tiler_src_pad_buffer_probe(pad, info, u_data):

#     gst_buffer = info.get_buffer()
#     if not gst_buffer:
#         print("Unable to get GstBuffer ")
#         return

#     # Retrieve batch metadata from the gst_buffer
#     # Note that pyds.gst_buffer_get_nvds_batch_meta() expects the
#     # C address of gst_buffer as input, which is obtained with hash(gst_buffer)
    

#     return Gst.PadProbeReturn.OK


# def cb_newpad(decodebin, decoder_src_pad, data):
#     print("In cb_newpad\n")
#     caps = decoder_src_pad.get_current_caps()
#     gststruct = caps.get_structure(0)
#     gstname = gststruct.get_name()
#     source_bin = data
#     features = caps.get_features(0)

#     # Need to check if the pad created by the decodebin is for video and not
#     # audio.
#     print("gstname=", gstname)
#     # if gstname.find("video") != -1:
#     #     # Link the decodebin pad only if decodebin has picked nvidia
#     #     # decoder plugin nvdec_*. We do this by checking if the pad caps contain
#     #     # NVMM memory features.
#     #     print("features=", features)
#     #     if features.contains("memory:NVMM"):
#     #         # Get the source bin ghost pad
#     #         bin_ghost_pad = source_bin.get_static_pad("src")
#     #         if not bin_ghost_pad.set_target(decoder_src_pad):
#     #             sys.stderr.write(
#     #                 "Failed to link decoder src pad to source bin ghost pad\n"
#     #             )
#     #     else:
#     #         sys.stderr.write(
#     #             " Error: Decodebin did not pick nvidia decoder plugin.\n")


# def decodebin_child_added(child_proxy, Object, name, user_data):
#     print("Decodebin child added:", name, "\n")
#     if name.find("decodebin") != -1:
#         Object.connect("child-added", decodebin_child_added, user_data)


# def create_source_bin(index, uri):
#     print("Creating source bin")

#     # Create a source GstBin to abstract this bin's content from the rest of the
#     # pipeline
#     bin_name = "source-bin-%02d" % index
#     print(bin_name)
#     nbin = Gst.Bin.new(bin_name)
#     if not nbin:
#         sys.stderr.write(" Unable to create source bin \n")

#     # Source element for reading from the uri.
#     # We will use decodebin and let it figure out the container format of the
#     # stream and the codec and plug the appropriate demux and decode plugins.
#     uri_decode_bin = Gst.ElementFactory.make("uridecodebin", "uri-decode-bin")
#     if not uri_decode_bin:
#         sys.stderr.write(" Unable to create uri decode bin \n")
#     # We set the input uri to the source element
#     uri_decode_bin.set_property("uri", uri)
#     # Connect to the "pad-added" signal of the decodebin which generates a
#     # callback once a new pad for raw data has beed created by the decodebin
#     uri_decode_bin.connect("pad-added", cb_newpad, nbin)
#     uri_decode_bin.connect("child-added", decodebin_child_added, nbin)

#     # We need to create a ghost pad for the source bin which will act as a proxy
#     # for the video decoder src pad. The ghost pad will not have a target right
#     # now. Once the decode bin creates the video decoder and generates the
#     # cb_newpad callback, we will set the ghost pad target to the video decoder
#     # src pad.
#     Gst.Bin.add(nbin, uri_decode_bin)
#     bin_pad = nbin.add_pad(
#         Gst.GhostPad.new_no_target(
#             "src", Gst.PadDirection.SRC))
#     if not bin_pad:
#         sys.stderr.write(" Failed to add ghost pad in source bin \n")
#         return None
#     return nbin


# def main(args):
#     # Check input arguments
#     number_sources = len(args)

#     # Standard GStreamer initialization
#     Gst.init(None)

#     # Create gstreamer elements */
#     # Create Pipeline element that will form a connection of other elements
#     print("Creating Pipeline \n ")
#     pipeline = Gst.Pipeline()
#     is_live = False

#     if not pipeline:
#         sys.stderr.write(" Unable to create Pipeline \n")

#     # print("Creating streamux \n ")
#     # Create nvstreammux instance to form batches from one or more sources.
#     # streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
#     # if not streammux:
#     #     sys.stderr.write(" Unable to create NvStreamMux \n")

#     # pipeline.add(streammux)

#     for i in range(number_sources):
#         print("Creating source_bin ", i, " \n ")
#         uri_name = args[i]
#         if uri_name.find("rtsp://") == 0:
#             is_live = True
#         source_bin = create_source_bin(i, uri_name)
#         if not source_bin:
#             sys.stderr.write("Unable to create source bin \n")
#         pipeline.add(source_bin)

#         # padname = "sink_%u" % i
#         # sinkpad = streammux.get_request_pad(padname)
#         # if not sinkpad:
#         #     sys.stderr.write("Unable to create sink pad bin \n")

#         # srcpad = source_bin.get_static_pad("src")
#         # if not srcpad:
#         #     sys.stderr.write("Unable to create src pad bin \n")

#         # srcpad.link(sinkpad)

#     # print("Creating Pgie \n ")
#     # if gie=="nvinfer":
#     #     pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
#     # else:
#     #     pgie = Gst.ElementFactory.make("nvinferserver", "primary-inference")
#     # if not pgie:
#     #     sys.stderr.write(" Unable to create pgie \n")
#     # print("Creating tiler \n ")
#     # tiler = Gst.ElementFactory.make("nvmultistreamtiler", "nvtiler")
#     # if not tiler:
#     #     sys.stderr.write(" Unable to create tiler \n")
#     # print("Creating nvvidconv \n ")
#     # nvvidconv = Gst.ElementFactory.make("nvvideoconvert", "convertor")
#     # if not nvvidconv:
#     #     sys.stderr.write(" Unable to create nvvidconv \n")
#     # print("Creating nvosd \n ")
#     # nvosd = Gst.ElementFactory.make("nvdsosd", "onscreendisplay")
#     # if not nvosd:
#     #     sys.stderr.write(" Unable to create nvosd \n")
#     # nvvidconv_postosd = Gst.ElementFactory.make(
#     #     "nvvideoconvert", "convertor_postosd")
#     # if not nvvidconv_postosd:
#     #     sys.stderr.write(" Unable to create nvvidconv_postosd \n")

#     # Create a caps filter
#     caps = Gst.ElementFactory.make("capsfilter", "filter")
#     caps.set_property(
#         "caps", Gst.Caps.from_string("video/x-raw(memory:NVMM), format=RGBA") # RGBA for CPU, I420 for GPU
#     )

#     # Make the encoder
#     # if codec == "H264":
#     #     encoder = Gst.ElementFactory.make("nvv4l2h264enc", "encoder")
#     #     print("Creating H264 Encoder")
#     # elif codec == "H265":
#     #     encoder = Gst.ElementFactory.make("nvv4l2h265enc", "encoder")
#     #     print("Creating H265 Encoder")
#     # if not encoder:
#     #     sys.stderr.write(" Unable to create encoder")
#     # encoder.set_property("bitrate", bitrate)
#     # if is_aarch64():
#     #     encoder.set_property("preset-level", 1)
#     #     encoder.set_property("insert-sps-pps", 1)
#     #     #encoder.set_property("bufapi-version", 1)

#     # Make the payload-encode video into RTP packets
#     if codec == "H264":
#         rtppay = Gst.ElementFactory.make("rtph264pay", "rtppay")
#         print("Creating H264 rtppay")
#     elif codec == "H265":
#         rtppay = Gst.ElementFactory.make("rtph265pay", "rtppay")
#         print("Creating H265 rtppay")
#     if not rtppay:
#         sys.stderr.write(" Unable to create rtppay")

#     # Make the UDP sink
#     updsink_port_num = 5400
#     sink = Gst.ElementFactory.make("udpsink", "udpsink")
#     if not sink:
#         sys.stderr.write(" Unable to create udpsink")

#     sink.set_property("host", "224.224.255.255")
#     sink.set_property("port", updsink_port_num)
#     sink.set_property("async", False)
#     sink.set_property("sync", 1)

#     # streammux.set_property("width", 1920)
#     # streammux.set_property("height", 1080)
#     # streammux.set_property("batch-size", 1)
#     # streammux.set_property("batched-push-timeout", 4000000)

#     # if gie=="nvinfer":
#     #     pgie.set_property("config-file-path", "dstest1_pgie_config.txt")
#     # else:
#     #     pgie.set_property("config-file-path", "dstest1_pgie_inferserver_config.txt")


#     # pgie_batch_size = pgie.get_property("batch-size")
#     # if pgie_batch_size != number_sources:
#     #     print(
#     #         "WARNING: Overriding infer-config batch-size",
#     #         pgie_batch_size,
#     #         " with number of sources ",
#     #         number_sources,
#     #         " \n",
#     #     )
#     #     pgie.set_property("batch-size", number_sources)

#     print("Adding elements to Pipeline \n")
#     # tiler_rows = int(math.sqrt(number_sources))
#     # tiler_columns = int(math.ceil((1.0 * number_sources) / tiler_rows))
#     # tiler.set_property("rows", tiler_rows)
#     # tiler.set_property("columns", tiler_columns)
#     # tiler.set_property("width", TILED_OUTPUT_WIDTH)
#     # tiler.set_property("height", TILED_OUTPUT_HEIGHT)
#     # sink.set_property("qos", 0)

#     # pipeline.add(pgie)
#     # pipeline.add(tiler)
#     # pipeline.add(nvvidconv)
#     # pipeline.add(nvosd)
#     # pipeline.add(nvvidconv_postosd)
#     pipeline.add(caps)
#     # pipeline.add(encoder)
#     pipeline.add(rtppay)
#     pipeline.add(sink)

#     # streammux.link(pgie)
#     # pgie.link(nvvidconv)
#     # nvvidconv.link(tiler)
#     # tiler.link(nvosd)
#     # nvosd.link(nvvidconv_postosd)
#     # nvvidconv_postosd.link(caps)
#     caps.link(rtppay)
#     # encoder.link(rtppay)
#     rtppay.link(sink)

#     # create an event loop and feed gstreamer bus mesages to it
#     loop = GLib.MainLoop()
#     bus = pipeline.get_bus()
#     bus.add_signal_watch()
#     # bus.connect("message", bus_call, loop)

#     # Start streaming
#     rtsp_port_num = 8554

#     server = GstRtspServer.RTSPServer.new()
#     server.props.service = "%d" % rtsp_port_num
#     server.attach(None)

#     factory = GstRtspServer.RTSPMediaFactory.new()
#     factory.set_launch(
#         '( udpsrc name=pay0 port=%d buffer-size=524288 caps="application/x-rtp, media=video, clock-rate=90000, encoding-name=(string)%s, payload=96 " )'
#         % (updsink_port_num, codec)
#     )
#     factory.set_shared(True)
#     server.get_mount_points().add_factory("/ds-test", factory)

#     print(
#         "\n *** DeepStream: Launched RTSP Streaming at rtsp://localhost:%d/ds-test ***\n\n"
#         % rtsp_port_num
#     )

#     # start play back and listen to events
#     print("Starting pipeline \n")
#     pipeline.set_state(Gst.State.PLAYING)
#     try:
#         loop.run()
#     except BaseException:
#         pass
#     # cleanup
#     pipeline.set_state(Gst.State.NULL)


# def parse_args():
#     parser = argparse.ArgumentParser(description='RTSP Output Sample Application Help ')
#     parser.add_argument("-i", "--input",
#                   help="Path to input H264 elementry stream", nargs="+", default=["rtsp://admin:Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0"], required=True)
#     # parser.add_argument("-g", "--gie", default="nvinfer",
#     #               help="choose GPU inference engine type nvinfer or nvinferserver , default=nvinfer", choices=['nvinfer','nvinferserver'])
#     parser.add_argument("-c", "--codec", default="H264",
#                   help="RTSP Streaming Codec H264/H265 , default=H264", choices=['H264','H265'])
#     # parser.add_argument("-b", "--bitrate", default=4000000,
#     #               help="Set the encoding bitrate ", type=int)
#     # Check input arguments
#     if len(sys.argv)==1:
#         parser.print_help(sys.stderr)
#         sys.exit(1)
#     args = parser.parse_args()
#     global codec
#     # global bitrate
#     global stream_path
#     # global gie
#     # gie = args.gie
#     codec = args.codec
#     # bitrate = args.bitrate
#     stream_path = args.input
#     return stream_path

# if __name__ == '__main__':
#     stream_path = parse_args()
#     sys.exit(main(stream_path))


# # python3 gstreamer_camera5.py -i 'rtsp://admin:Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0' -c 'H264'



# # import required libraries
# from vidgear.gears import CamGear
# import cv2

# # add rstp source with multiple streams
RSTP_source_location = "rtsp://admin:Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0"

# # define gstreamer pipeline
# gstreamer_source = ('rtspsrc location={} latency=300 !' \
#         ' rtph264depay !' \
#         ' h264parse !'.format(RSTP_source_location))

# print('gst-launch-1.0 ', str(gstreamer_source))

# # gstreamer_source = ('appsrc name=source is-live=true block=true format=GST_FORMAT_TIME ' \
# #                     'caps=video/x-raw,format=BGR,width={},height={},framerate={}/1 ' \
# #                     '! videoconvert ' \
# #                     '! video/x-raw,format=I420 ' \
# #                     '! x264enc speed-preset=ultrafast tune=zerolatency ' \
# #                     '! rtph264pay config-interval=1 name=pay0 pt=96' \
# #                     .format(self.width, self.height, self.fps))

# # Add gstreamer source and enable backend
# stream = CamGear(source=RSTP_source_location , logging=True, backend=cv2.CAP_GSTREAMER).start() 

# # loop over
# while True:

#     # read frames from stream
#     frame = stream.read()

#     # check for frame if Nonetype
#     if frame is None:
#         break


#     # {do something with the frame here}


#     # Show output window
#     cv2.imshow("Output Frame", frame)

#     # check for 'q' key if pressed
#     key = cv2.waitKey(1) & 0xFF
#     if key == ord("q"):
#         break

# # close output window
# cv2.destroyAllWindows()

# # safely close video stream
# stream.stop()
# # safely close video stream.



# import gi
# gi.require_version('Gst', '1.0')
# from gi.repository import Gst, GObject, GLib

# Gst.init(None)

# pipeline = Gst.Pipeline()

# source = Gst.ElementFactory.make('rtspsrc', 'source')
# source.set_property('location', 'rtsp://admin:Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0')

# decode = Gst.ElementFactory.make('decodebin', 'decode')

# videoconvert = Gst.ElementFactory.make('videoconvert', 'videoconvert')

# sink = Gst.ElementFactory.make('autovideosink', 'sink')

# pipeline.add(source)
# pipeline.add(decode)
# pipeline.add(videoconvert)
# pipeline.add(sink)

# source.link(decode)
# # decode.connect('pad-added', lambda decode, pad: pad.link(videoconvert.get_static_pad('sink')))
# decode.link(videoconvert)
# videoconvert.link(sink)

# pipeline.set_state(Gst.State.PLAYING)

# mainloop = GLib.MainLoop()
# try:
#     mainloop.run()
# except KeyboardInterrupt:
#     pass

# pipeline.set_state(Gst.State.NULL)



import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

Gst.init(None)

pipeline = Gst.Pipeline()

videotestsrc = Gst.ElementFactory.make('videotestsrc', 'test-video')
videotestsrc.set_property('pattern', 0)

x264enc = Gst.ElementFactory.make('x264enc', 'x264-encoder')

rtph264pay = Gst.ElementFactory.make('rtph264pay', 'h264-payloader')

rtspclientsink = Gst.ElementFactory.make('rtspclientsink', 'rtsp-output')
rtspclientsink.set_property('location', 'rtsp://127.0.0.1:8554/test')

pipeline.add(videotestsrc)
pipeline.add(x264enc)
pipeline.add(rtph264pay)
pipeline.add(rtspclientsink)

videotestsrc.link(x264enc)
x264enc.link(rtph264pay)
rtph264pay.link(rtspclientsink)

pipeline.set_state(Gst.State.PLAYING)

bus = pipeline.get_bus()
msg = bus.timed_pop_filtered(Gst.CLOCK_TIME_NONE, Gst.MessageType.ERROR | Gst.MessageType.EOS)

pipeline.set_state(Gst.State.PLAYING)

mainloop = GLib.MainLoop()
try:
    mainloop.run()
except KeyboardInterrupt:
    pass

pipeline.set_state(Gst.State.NULL)