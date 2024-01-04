import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GObject, GLib, GstRtspServer

Gst.init(None)

pipeline = Gst.Pipeline()

# # Add an RTSP source element
# rtspsrc = Gst.ElementFactory.make("rtspsrc", "source")
# rtspsrc.set_property("location", "rtsp://admin:Rapidev321@192.168.23.166:554cam/realmonitor?channel=1&subtype=0")

# # Add a decodebin element to decode the video stream
# decodebin = Gst.ElementFactory.make("decodebin", "decoder")

# # Add a videoconvert element to convert the video format
# videoconvert = Gst.ElementFactory.make("videoconvert", "convert")

# # Add an x264enc element to encode the video stream
# x264enc = Gst.ElementFactory.make("x264enc", "encoder")
# x264enc.set_property("speed-preset", 2)

# # Add a rtph264pay element to packetize the encoded video
# rtph264pay = Gst.ElementFactory.make("rtph264pay", "payloader")
# rtph264pay.set_property("pt", 96)

# # Add a udpsink element to send the packetized video over UDP
# udpsink = Gst.ElementFactory.make("udpsink", "udpsink")
# # udpsink.set_property("host", "192.168.18.229")
# udpsink.set_property("host", "224.224.255.255")
# udpsink.set_property("port", 5000)

# # # Add an RTSP server to publish the stream with a custom path
# # rtsp_server = Gst.ElementFactory.make("rtspsink", "rtsp-server")
# # if not rtsp_server:
# #     print("Error: Could not create rtspsink element")
# #     exit(1)

# # rtsp_server.set_property("port", 8556)
# # rtsp_server.set_property("location", "/stream")
# # rtsp_server.set_property("protocols", "tcp")

# # Add all elements to the pipeline
# pipeline.add(rtspsrc)
# pipeline.add(decodebin)
# pipeline.add(videoconvert)
# pipeline.add(x264enc)
# pipeline.add(rtph264pay)
# pipeline.add(udpsink)


# # Link the elements together
# rtspsrc.link(decodebin)
# decodebin.link(videoconvert)
# videoconvert.link(x264enc)
# x264enc.link(rtph264pay)
# rtph264pay.link(udpsink)

# # rtsp_server = GstRtspServer.RTSPServer()
# # factory = RtspMediaFactory(filename=args.file)
# # factory.set_shared(True)
# # mount_points = rtsp_server.get_mount_points()
# # mount_points.add_factory("/Stream/", factory)
# # rtsp_server.attach(None)

# rtsp_server = GstRtspServer.RTSPServer.new()
# rtsp_server.props.service = "8556"
# rtsp_server.attach(None)

# # pipeline.add(rtsp_server)

# factory = GstRtspServer.RTSPMediaFactory.new()
# # factory.set_launch(pipeline)
# factory.set_launch(
#     '( udpsrc name=pay0 port=%d buffer-size=524288 caps="application/x-rtp, media=video, clock-rate=90000, encoding-name=(string)%s, payload=96 " )'
#     % (5000, "H264")
# )
# factory.set_shared(True)

# rtsp_server.get_mount_points().add_factory("/stream", factory)

# # Start the pipeline
# pipeline.set_state(Gst.State.PLAYING)

# # Run the pipeline
# loop = GObject.MainLoop()
# loop.run()







class MyFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self):
        GstRtspServer.RTSPMediaFactory.__init__(self)
        self.pipeline = None

    def do_create_element(self, url):
        if not self.pipeline:
            src = Gst.ElementFactory.make("videotestsrc", "source")
            enc = Gst.ElementFactory.make("x264enc", "encoder")
            sink = Gst.ElementFactory.make("udpsink", "sink")
            sink.set_property("host", "127.0.0.1")
            sink.set_property("port", 5000)
            self.pipeline = Gst.Pipeline.new("mypipeline")
            self.pipeline.add(src)
            self.pipeline.add(enc)
            self.pipeline.add(sink)
            src.link(enc)
            enc.link(sink)
        return self.pipeline

# Gst.init(None)
server = GstRtspServer.RTSPServer()
server.set_service("8554")
factory = MyFactory()
factory.set_shared(True)
server.get_mount_points().add_factory("/test", factory)
server.attach(None)

print("RTSP server ready at rtsp://127.0.0.1:8554/test")
# print("Pipeline string: {}".format(server.get_mount_points().get_mountpoint("/test").get_element().get_request_uri()))
print("Pipeline string: {}".format(server.get_mount_points().add_factory("/test", factory)))
loop = GObject.MainLoop()
loop.run()



# class MyFactory(GstRtspServer.RTSPMediaFactory):
#     def __init__(self):
#         GstRtspServer.RTSPMediaFactory.__init__(self)

#     def do_create_element(self, url):
#         source = Gst.ElementFactory.make("v4l2src")
#         caps = Gst.Caps.from_string("video/x-raw,width=640,height=480")
#         sourcefilter = Gst.ElementFactory.make("capsfilter", "sourcefilter")
#         sourcefilter.set_property("caps", caps)
#         h264encoder = Gst.ElementFactory.make("x264enc")
#         rtph264pay = Gst.ElementFactory.make("rtph264pay")
#         sink = Gst.ElementFactory.make("udpsink")
#         sink.set_property("host", "127.0.0.1")
#         sink.set_property("port", "5000")
#         pipeline = Gst.Pipeline()
#         pipeline.add(source)
#         pipeline.add(sourcefilter)
#         pipeline.add(h264encoder)
#         pipeline.add(rtph264pay)
#         pipeline.add(sink)
#         source.link(sourcefilter)
#         sourcefilter.link(h264encoder)
#         h264encoder.link(rtph264pay)
#         rtph264pay.link(sink)
#         return pipeline

# def main():
#     GObject.threads_init()
#     Gst.init(None)

#     # Create a new instance of the RTSP server
#     server = GstRtspServer.RTSPServer()

#     # Set the server port number
#     server.set_service("8554")

#     # Create a new media factory for the server
#     factory = MyFactory()

#     # Set the RTSP path of the factory
#     factory.set_launch("( v4l2src ! capsfilter caps=\"video/x-raw,width=640,height=480\" ! x264enc ! rtph264pay name=pay0 pt=96 )")

#     # Add the factory to the server's mount points
#     server.get_mount_points().add_factory("/test", factory)

#     # Start the server
#     server.attach(None)

#     # Print the pipeline string for the server
#     print("Pipeline string: {}".format(factory.get_element().get_request_uri(None, None)))

#     loop = GObject.MainLoop()
#     loop.run()

# if __name__ == '__main__':
#     main()



# class MyFactory(GstRtspServer.RTSPMediaFactory):
#     def __init__(self, **properties):
#         super(MyFactory, self).__init__(**properties)
#         self.pipeline = None
#         self.bus = None
#         self.mainloop = None

#     def do_create_element(self, url):
#         # create element to read from uridecodebin
#         # src_elem = Gst.ElementFactory.make("uridecodebin", None)
#         src_elem = Gst.ElementFactory.make("uridecodebin", "uri-decode-bin")

#         self.pipeline.add(src_elem)

#         # add event listeners
#         self.bus = self.pipeline.get_bus()
#         # self.bus.add_signal_watch()
#         # self.bus.connect("message", self.on_message)

#         # add the element to the pipeline and link
#         # self.pipeline.add(src_elem)
#         src_elem.link(self)

#         return self.pipeline

#     def do_configure(self, rtsp_media):
#         self.pipeline.set_state(Gst.State.PLAYING)

#     def on_message(self, bus, message):
#         t = message.type
#         if t == Gst.MessageType.EOS:
#             print("End-of-stream")
#             self.pipeline.set_state(Gst.State.NULL)
#             self.mainloop.quit()

#         elif t == Gst.MessageType.ERROR:
#             err, debug = message.parse_error()
#             print("Error: %s" % err, debug)
#             self.pipeline.set_state(Gst.State.NULL)
#             self.mainloop.quit()

# def main():
#     # GObject.threads_init()
#     Gst.init(None)

#     server = GstRtspServer.RTSPServer()
#     server.set_service("8554")
#     server.set_address("192.168.18.229")
#     # server.set_h264_enabled(True)

#     my_factory = MyFactory()
#     # my_factory = GstRtspServer.RTSPMediaFactory()
#     my_factory.set_shared(True)
#     server.get_mount_points().add_factory("/stream", my_factory)

#     # create pipeline string for printing
#     pipeline_str = "rtspsrc location={} ! rtph264depay ! h264parse ! queue ! rtph264pay name=pay0 pt=96".format("'rtsp://admin:Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0'")

#     # create pipeline for MyFactory
#     my_factory.pipeline = Gst.parse_launch(pipeline_str)
#     my_factory.mainloop = GObject.MainLoop()

#     print("Pipeline string: {} {}".format("gst-launch-1.0", pipeline_str))
#     server.attach(None)

#     my_factory.mainloop.run()

# if __name__ == '__main__':
#     main()



# import sys
# def bus_call(bus, message, loop):
#     # print(len(g_source_bin_list))
#     global g_eos_list
#     t = message.type
#     if t == Gst.MessageType.EOS:
#         sys.stdout.write("End-of-stream\n")
#         # loop.quit()
#     elif t==Gst.MessageType.WARNING:
#         err, debug = message.parse_warning()
#         sys.stderr.write("Warning: %s: %s\n" % (err, debug))
#     elif t == Gst.MessageType.ERROR:
#         err, debug = message.parse_error()
#         sys.stderr.write("Error: %s: %s\n" % (err, debug))
#         # loop.quit()
#     elif t == Gst.MessageType.INFO:
#         err, debug = message.parse_info()
#         sys.stderr.write("Error: %s: %s\n" % (err, debug))
#         # loop.quit()
#     elif t == Gst.MessageType.ELEMENT:
#         struct = message.get_structure()
#         # Check for stream-eos message
#         if struct is not None and struct.has_name("stream-eos"):
#             parsed, stream_id = struct.get_uint("stream-id")
#             if parsed:
#                 print("Got EOS from stream %d" % stream_id)
#     return True

# def on_rtspsrc_pad_added(r,  pad):
#     r.link(queue)
#     queue.link(rtph264depay)
#     rtph264depay.link(h264parse)
    # h264parse.link(mpegtsmux)
    # mpegtsmux.link(filesink)

# GObject.threads_init()
# Gst.init(None)

# pipeline = Gst.Pipeline()

# stream = "rtsp://admin:Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0"

# rtspsrc = Gst.ElementFactory.make("rtspsrc", "rtspsrc")
# if not rtspsrc:
#     sys.stderr.write(" Unable to create rtspsrc  \n".format())
# rtspsrc.set_property("location", str(stream))
# rtspsrc.set_property("latency", 10)
# # rtspsrc.set_property("do-rtsp-keep-alive", 1)
# # rtspsrc.connect("pad-added", on_rtspsrc_pad_added)
# pipeline.add(rtspsrc)

# # queue = Gst.ElementFactory.make("queue", "queue")
# # if not queue:
# #     sys.stderr.write(" Unable to create queue \n")
# # pipeline.add(queue)

# rtph264depay = Gst.ElementFactory.make("rtph264depay", "rtph264depay")
# if not rtph264depay:
#     sys.stderr.write(" Unable to create rtph264depay \n")
# pipeline.add(rtph264depay)

# h264parse = Gst.ElementFactory.make("h264parse", "h264parse")
# if not h264parse:
#     sys.stderr.write(" Unable to create h264parse \n")
# pipeline.add(h264parse)

# rtph64pay = Gst.ElementFactory.make("rtph264pay", "rtppay")
# if not rtph64pay:
#     sys.stderr.write(" Unable to create rtph64pay \n")
# pipeline.add(rtph64pay)

# udpsink = Gst.ElementFactory.make("udpsink", "udpsink")
# if not udpsink:
#     sys.stderr.write(" Unable to create udpsink \n")   
# udpsink.set_property("host", "224.224.255.255")
# udpsink.set_property("port", 5400)
# # udpsink.set_property("async", False)
# # udpsink.set_property("sync", 1)
# pipeline.add(udpsink)

# # sink = Gst.ElementFactory.make("udpsink")
# # sink.set_property("host", "127.0.0.1")
# # sink.set_property("port", "5000")
# # pipeline.add(sink)

# # # mpegtsmux = Gst.ElementFactory.make("mpegtsmux", "mpegtsmux")
# # # if not mpegtsmux:
# # #     sys.stderr.write(" Unable to create mpegtsmux \n")
# # # pipeline.add(mpegtsmux)

# # # filesink = Gst.ElementFactory.make("filesink", "filesink")
# # # if not filesink:
# # #     sys.stderr.write(" Unable to create filesink \n")
# # # filesink.set_property("location", "output.mp4")
# # # pipeline.add(filesink)

# # # decodebin = Gst.ElementFactory.make("decodebin", "decodebin")
# # # if not decodebin:
# # #     sys.stderr.write(" unable to create decodebin \n")
# # # pipeline.add(decodebin)

# # Add a decodebin element to decode the video stream
# # decodebin = Gst.ElementFactory.make("decodebin", "decoder")
# # pipeline.add(decodebin)

# # Add a videoconvert element to convert the video format
# # videoconvert = Gst.ElementFactory.make("videoconvert", "convert")
# # pipeline.add(videoconvert)

# # Add an x264enc element to encode the video stream
# # x264enc = Gst.ElementFactory.make("x264enc", "encoder")
# # x264enc.set_property("speed-preset", 2)
# # pipeline.add(x264enc)

# # Add a rtph264pay element to packetize the encoded video
# # rtph264pay = Gst.ElementFactory.make("rtph264pay", "payloader")
# # # rtph264pay.set_property("pt", 96)
# # pipeline.add(rtph264pay)

# # Add a udpsink element to send the packetized video over UDP
# # udpsink = Gst.ElementFactory.make("udpsink", "sink")
# # udpsink.set_property("host", "192.168.18.229")
# # udpsink.set_property("port", 5000)

# # # Add all elements to the pipeline
# # pipeline.add(udpsink)

# # Link the elements together
# # rtspsrc.link(decodebin)
# # decodebin.link(videoconvert)
# # videoconvert.link(x264enc)
# # x264enc.link(rtph264pay)
# # rtph264pay.link(udpsink)
# # rtph264pay.link(rtsp_server)

# rtspsrc.link(rtph264depay)
# rtph264depay.link(h264parse)
# h264parse.link(rtph64pay)
# rtph64pay.link(udpsink)

# if not pipeline:
#     sys.stderr.write(" Unable to create Pipeline \n")

# pipeline.set_state(Gst.State.PLAYING)

# # Create a new instance of the RTSP server
# server = GstRtspServer.RTSPServer()

# # Set the server port number
# server.set_service("8556")

# # Create a new media factory for the server
# # factory = pipeline()
# factory = GstRtspServer.RTSPMediaFactory.new()

# # Set the RTSP path of the factory
# factory.set_launch("rtspsrc location='rtsp://admin:Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0' latency=0 ! rtph264depay ! h264parse ! rtph264pay name=pay0 pt=96 ! udpsink host=192.168.18.229 port=5005")

# # factory.set_launch('( udpsrc name=pay0 port=5400 buffer-size=524288 caps="application/x-rtp,media=video,clock-rate=90000,encoding-name=H264,payload=96" )')

# # Add the factory to the server's mount points
# server.get_mount_points().add_factory("/stream", factory)

# # Start the server
# server.attach(None)



# loop = GLib.MainLoop()
# # # bus = pipeline.get_bus()
# # # bus.add_signal_watch()
# # # bus.connect("message", bus_call, loop)

# # rtsp_port_num = 8554
# # server = GstRtspServer.RTSPServer()
# # server.props.service = "%d" % rtsp_port_num
# # server.attach(None)

# # # factory = GstRtspServer.RTSPMediaFactory()
# # # factory.set_launch(
# # #     '( udpsrc name=pay0 port=%d buffer-size=524288 caps="application/x-rtp, media=video, clock-rate=90000, encoding-name=(string)%s, payload=96 " )'
# # #     % (5400, "H264")
# # # )
# # pipeline.set_shared(True)
# # server.get_mount_points().add_factory("/stream", pipeline)


# print("Starting pipeline \n")
# loop.run()


# # pipeline.set_state(Gst.State.PLAYING)
# # try:
# #     loop.run()
# #     print("running")
# # except BaseException:
# #     # logging.error("something went wrong")
# #     pass
# # pipeline.set_state(Gst.State.NULL)
# # loop.run()