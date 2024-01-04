import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib

# Gst.init(None)

# class MyFactory(GstRtspServer.RTSPMediaFactory):
#     def __init__(self, uri, **properties):
#         # GstRtspServer.RTSPMediaFactory.__init__(self)
#         super(MyFactory, self).__init__(**properties)
#         self.uri = uri
#         self.pipeline = Gst.Pipeline()

#     #Live streaming and detection
#     def on_need_data(self, src, length):
        
#         if self.cap.isOpened():
#             ret, frame = self.cap.read()
#             if ret:
#                 # print(frame.shape)
#                 # img0 = frame  # BGR
#                 # # Padded resize
#                 # img = non_sattelite_model.letterbox(img0, non_sattelite_model.img_size, stride=non_sattelite_model.stride)[0]
#                 # # Convert
#                 # img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
#                 # img = np.ascontiguousarray(img)
#                 # source = img #np.expand_dims(frame, 0)

#                 # data = frame
#                 data = frame.tobytes()
#                 buf = Gst.Buffer.new_allocate(None, len(data), None)
#                 buf.fill(0, data)
#                 buf.duration = self.duration
#                 timestamp = self.number_frames * self.duration
#                 buf.pts = buf.dts = int(timestamp)
#                 buf.offset = timestamp
#                 self.counter += 1
#                 self.number_frames += 1
#                 retval = src.emit('push-buffer', buf)
#                 print('pushed buffer, frame {}, duration {} ns, durations {} s'.format(self.number_frames,
#                                                                                        self.duration,
#                                                                                        self.duration / Gst.SECOND))
#                 if retval != Gst.FlowReturn.OK:
#                     print(retval)
    

#     def do_create_element(self, uri):
#         src = Gst.ElementFactory.make('rtspsrc', None)
#         src.set_property('location', self.uri)
#         depay = Gst.ElementFactory.make("rtph264depay", None)
#         par = Gst.ElementFactory.make("h264parse", None)
#         pay = Gst.ElementFactory.make("rtph264pay", None)
#         sink = Gst.ElementFactory.make("udpsink", None)
#         sink.set_property("host", "127.0.0.1")
#         sink.set_property("port", 5400)

#         self.pipeline.add(src)
#         self.pipeline.add(depay)
#         self.pipeline.add(par)
#         self.pipeline.add(pay)
#         self.pipeline.add(sink)

#         src.link(depay)
#         depay.link(par)
#         par.link(pay)
#         pay.link(sink)

#         # return self.pipeline


# class GstServer(GstRtspServer.RTSPServer):
#     port = 8556
#     stream_uri = "/video_stream"

#     def __init__(self, **properties):
#         super(GstServer, self).__init__(**properties)
#         rtsp_src = "rtsp://admin:Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0"
#         self.factory = MyFactory(rtsp_src)
#         self.factory.set_shared(True)
#         self.set_service(str(self.port)) # if port added then comment this line
#         self.get_mount_points().add_factory(self.stream_uri, self.factory)
#         self.attach(None)

# # server = GstRtspServer.RTSPServer()
# # server.props.service = "%d" % 8556
# # server.attach(None)
# # server.set_service("8554")
# # server.set_address("192.168.18.229")
# # server.set_h264_enabled(True)

# # factory = MyFactory()
# # factory.set_shared(True)
# # mounts = server.get_mount_points()
# # mounts.add_factory("/test", factory)
# # server.attach(None)

# print("RTSP server ready at rtsp://127.0.0.1:8556/video_stream")

# Gst.init(None)
# server = GstServer()
# loop = GLib.MainLoop()
# loop.run()


# class RTSPStream:
#     def __init__(self, rtsp_url):
#         self.rtsp_url = rtsp_url
#         self.pipeline = None
#         self.bus = None
#         self.mainloop = None

#     def start(self):
#         Gst.init(None)

#         # self.pipeline = Gst.parse_launch("rtspsrc location={} ! rtph264depay ! avdec_h264 ! videoconvert ! x264enc ! rtph264pay name=pay0 pt=96".format(self.rtsp_url))
#         self.pipeline = Gst.parse_launch("rtspsrc location={} ! rtph264depay".format(self.rtsp_url))
#         self.bus = self.pipeline.get_bus()

#         self.pipeline.set_state(Gst.State.PLAYING)

#         self.mainloop = GLib.MainLoop()

#         bus_watch_id = self.bus.add_signal_watch()
#         self.bus.connect("message::error", self.on_error)
#         self.bus.connect("message::eos", self.on_eos)
#         self.bus.connect("message::state-changed", self.on_state_changed)

#         self.mainloop.run()

#     def on_error(self, bus, message):
#         error = message.parse_error()
#         print("Error received from element {}: {}".format(message.src.get_name(), error))

#     def on_eos(self, bus, message):
#         print("End-Of-Stream reached")

#     def on_state_changed(self, bus, message):
#         old_state, new_state, pending_state = message.parse_state_changed()
#         print("Pipeline state changed from {} to {}".format(old_state.value_nick, new_state.value_nick))

#     def on_need_data(self, appsrc, unused_data):
#         sample = appsrc.emit("pull-sample")
#         if sample:
#             print("Frame received!")

#     def stop(self):
#         if self.pipeline:
#             self.pipeline.set_state(Gst.State.NULL)
#         if self.mainloop:
#             self.mainloop.quit()

class RTSPServer:
    def __init__(self, port, mount_point):
        self.port = port
        self.mount_point = mount_point
        self.server = None

    def start(self):
        Gst.init(None)

        self.server = GstRtspServer.RTSPServer()
        self.server.set_service(str(self.port))
        factory = GstRtspServer.RTSPMediaFactory()
        factory.set_launch("videotestsrc ! videoconvert ! x264enc ! rtph264pay name=pay0")
        # factory.set_launch("videotestsrc ! videoconvert ! x264enc ! rtph264pay name=pay0 pt=96")
        # factory.set_launch("videotestsrc ! video/x-raw,width=640,height=480 ! x264enc ! rtph264pay name=pay0 pt=96")
        # factory.set_launch("rtspsrc location='rtsp://admin:Admin12345@192.168.23.199:554' latency=0 ! rtph264depay ! rtph264pay name=pay0 pt=96")
        # factory.set_launch("uridecodebin uri='rtsp://admin:Admin12345@192.168.23.199:554' ! videoconvert ! x264enc ! rtph264pay name=pay0")
        # factory.set_launch("rtspsrc location='rtsp://admin:Admin12345@192.168.23.199:554' ! rtph264depay")
        self.server.get_mount_points().add_factory(self.mount_point, factory)
        self.server.attach(None)

        print("RTSP server started at rtsp://localhost:{}{}".format(self.port, self.mount_point))

    def stop(self):
        if self.server:
            self.server.detach()

if __name__ == '__main__':
    # stream = RTSPStream("rtsp://admin:Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0")
    server = RTSPServer(8558, "/test")
    server.start()
    # stream.start()

    loop = GLib.MainLoop()
    loop.run()




# import gi
# gi.require_version('Gst', '1.0')
# from gi.repository import GObject, Gst, GstRtspServer, GLib


# class RTSPCamera:
#     def __init__(self, uri):
#         self.uri = uri

#     def start(self):
#         Gst.init(None)
#         self.pipeline = Gst.Pipeline()
#         self.rtsp_src = Gst.ElementFactory.make('rtspsrc', None)
#         self.rtsp_src.set_property('location', self.uri)
#         self.rtsp_src.connect('pad-added', self.on_pad_added)
#         self.decodebin = Gst.ElementFactory.make('decodebin', None)
#         self.video_convert = Gst.ElementFactory.make('videoconvert', None)
#         self.sink = Gst.ElementFactory.make('autovideosink', None)
#         self.pipeline.add(self.rtsp_src)
#         self.pipeline.add(self.decodebin)
#         self.pipeline.add(self.video_convert)
#         self.pipeline.add(self.sink)
#         self.rtsp_src.link(self.decodebin)
#         self.decodebin.connect('pad-added', self.decodebin_on_pad_added)
#         self.video_convert.link(self.sink)
#         self.pipeline.set_state(Gst.State.PLAYING)

#     def on_pad_added(self, src, pad):
#         caps = pad.get_current_caps()
#         structure = caps.get_structure(0)
#         name = structure.get_name()
#         if name.startswith('video'):
#             self.videopad = self.decodebin.get_static_pad('sink')
#             pad.link(self.videopad)

#     def decodebin_on_pad_added(self, element, pad):
#         caps = pad.get_current_caps()
#         structure = caps.get_structure(0)
#         name = structure.get_name()
#         if name.startswith('video'):
#             pad.link(self.video_convert.get_static_pad('sink'))


# class RTSPServer:
#     def __init__(self, mount_path, port):
#         Gst.init(None)
#         self.server = GstRtspServer.RTSPServer.new()
#         self.mounts = self.server.get_mount_points()
#         self.factory = GstRtspServer.RTSPMediaFactory.new()
#         self.factory.set_launch('( appsrc name=source ! videoconvert ! x264enc tune=zerolatency ! rtph264pay name=pay0 pt=96 )')
#         self.factory.set_shared(True)
#         self.factory.set_buffer_size(1024)
#         self.mounts.add_factory(mount_path, self.factory)
#         self.server.props.service = str(port)
#         self.server.attach(None)

#     def run(self):
#         loop = GObject.MainLoop()
#         loop.run()


# if __name__ == '__main__':
#     camera = RTSPCamera('admin:Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0')
#     camera.start()

#     server = RTSPServer('/test', 8556)
#     server.run()





# import gi
# gi.require_version('Gst', '1.0')
# gi.require_version('GstRtspServer', '1.0')
# from gi.repository import GObject, Gst, GstRtspServer, GLib


# class CameraStream:
#     def __init__(self, rtsp_url):
#         self.rtsp_url = rtsp_url
#         self.pipeline = None

#         # Initialize GStreamer
#         Gst.init(None)

#         # Create pipeline
#         self.pipeline = Gst.Pipeline.new("camera-pipeline")

#         # Create elements
#         self.rtsp_src = Gst.ElementFactory.make("rtspsrc", "rtsp-source")
#         self.rtsp_src.set_property("location", self.rtsp_url)
#         self.decodebin = Gst.ElementFactory.make("decodebin", "decodebin")
#         self.video_convert = Gst.ElementFactory.make("videoconvert", "video-convert")
#         self.video_sink = Gst.ElementFactory.make("autovideosink", "video-sink")

#         # Add elements to the pipeline
#         self.pipeline.add(self.rtsp_src)
#         self.pipeline.add(self.decodebin)
#         self.pipeline.add(self.video_convert)
#         self.pipeline.add(self.video_sink)

#         # Link elements
#         self.rtsp_src.link(self.decodebin)
#         self.decodebin.connect("pad-added", self.on_decodebin_pad_added)
#         self.video_convert.link(self.video_sink)

#         # Start the pipeline
#         self.pipeline.set_state(Gst.State.PLAYING)

#     def on_decodebin_pad_added(self, decodebin, pad):
#         # Link decodebin to videoconvert
#         if pad.get_current_caps().to_string().startswith("video"):
#             decodebin_src_pad = decodebin.get_static_pad("src")
#             video_convert_sink_pad = self.video_convert.get_static_pad("sink")
#             decodebin_src_pad.link(video_convert_sink_pad)


# class RtspServer:
#     def __init__(self, camera_stream, port, mount_point):
#         self.camera_stream = camera_stream
#         self.port = port
#         self.mount_point = mount_point
#         self.pipeline = None

#         # Initialize GStreamer
#         Gst.init(None)

#         # Create pipeline
#         self.pipeline = Gst.Pipeline.new("rtsp-server-pipeline")

#         # Create elements
#         self.rtsp_src = Gst.ElementFactory.make("appsrc", "rtsp-source")
#         self.rtsp_jitterbuffer = Gst.ElementFactory.make("rtpjitterbuffer", "rtsp-jitterbuffer")
#         self.rtsp_depay = Gst.ElementFactory.make("rtph264depay", "rtsp-depay")
#         self.rtsp_parse = Gst.ElementFactory.make("h264parse", "rtsp-parse")
#         self.rtsp_pay = Gst.ElementFactory.make("rtph264pay", "rtsp-pay")
#         self.rtsp_sink = Gst.ElementFactory.make("udpsink", "rtsp-sink")
#         self.rtsp_server = Gst.ElementFactory.make("rtspsink", "rtsp-server")

#         # Set element properties
#         self.rtsp_sink.set_property("host", "127.0.0.1")
#         self.rtsp_sink.set_property("port", self.port)
#         self.rtsp_server.set_property("service", self.port)
#         self.rtsp_server.set_property("location", "/" + self.mount_point)

#         # Add elements to the pipeline
#         self.pipeline.add(self.rtsp_src)
#         self.pipeline.add(self.rtsp_jitterbuffer)
#         self.pipeline.add(self.rtsp_depay)
#         self.pipeline.add(self.rtsp_parse)
#         self.pipeline.add(self.rtsp_pay)
#         self.pipeline.add(self.rtsp_sink)
       
#         # Add elements to the pipeline
#         self.pipeline.add(self.rtsp_src)
#         self.pipeline.add(self.rtsp_jitterbuffer)
#         self.pipeline.add(self.rtsp_depay)
#         self.pipeline.add(self.rtsp_parse)
#         self.pipeline.add(self.rtsp_pay)
#         self.pipeline.add(self.rtsp_sink)
       


# class GstServer(GstRtspServer.RTSPServer):
#     def __init__(self, **properties):
#         super(GstServer, self).__init__(**properties)
#         self.factory = None
#         self.set_service(str(8554))
#         self.connect("client-connected", self.client_connected)

#     def set_factory(self, factory):
#         self.factory = factory

#     def client_connected(self, arg1, arg2):
#         print("Client connected")

# class MyFunction:
#     def __init__(self):
#         Gst.init(None)
#         self.pipeline = None
#         self.rtsp_server = None

#     def start_pipeline(self):
#         # self.rtsp_server = rtsp_server
#         self.pipeline = Gst.Pipeline()

#         source = Gst.ElementFactory.make("rtspsrc", "source")
#         source.set_property("location", "rtsp://admin:Rapidev321@192.168.23.166:554/")

#         depay = Gst.ElementFactory.make("rtph264depay", "depay")
#         decode = Gst.ElementFactory.make("decodebin", "decode")
#         convert = Gst.ElementFactory.make("videoconvert", "convert")
#         sink = Gst.ElementFactory.make("autovideosink", "sink")

#         self.pipeline.add(source)
#         self.pipeline.add(depay)
#         self.pipeline.add(decode)
#         self.pipeline.add(convert)
#         self.pipeline.add(sink)

#         source.link(depay)
#         depay.link(decode)
#         decode.link(convert)
#         convert.link(sink)

#         bus = self.pipeline.get_bus()
#         bus.add_signal_watch()
#         bus.connect("message::error", self.on_error)
#         bus.connect("message::state-changed", self.on_state_changed)

#         self.pipeline.set_state(Gst.State.PLAYING)

#     def on_state_changed(self, bus, message):
#         if message.src != self.pipeline:
#             return
#         old_state, new_state, pending_state = message.parse_state_changed()
#         print("Pipeline state changed from {} to {}".format(
#             Gst.Element.state_get_name(old_state), Gst.Element.state_get_name(new_state)))

#         if new_state == Gst.State.PLAYING:
#             print("Pipeline is now live")

#             # Add the pipeline to the RTSP server
#             factory = GstRtspServer.RTSPMediaFactory.new()
#             factory.set_element(self.pipeline)
#             factory.set_shared(True)
#             mount_points = self.get_mount_points()
#             mount_points.add_factory("/test", factory)
#             print("Pipeline string: {}".format(mount_points.get_mountpoint("/test").get_element().get_request_uri()))

#     def on_error(self, bus, message):
#         error, debug_info = message.parse_error()
#         print("Error received from element {}: {}".format(message.src.get_name(), error))
#         print("Debugging information: {}".format(debug_info))

#     def stop_pipeline(self):
#         if self.pipeline:
#             self.pipeline.set_state(Gst.State.NULL)
#             self.pipeline = None
#             print("Pipeline stopped")

# class GstServer:
#     def __init__(self, port, path):
#         self.pipeline = Gst.Pipeline()
#         self.server = GstRtspServer.RTSPServer()
#         self.server.set_service(str(port))
#         self.mounts = self.server.get_mount_points()
#         self.factory = GstRtspServer.RTSPMediaFactory()
#         self.factory.set_launch('( udpsrc port=5000 caps=application/x-rtp ! rtph264depay ! h264parse ! rtph264pay name=pay0 pt=96 )')
#         self.mounts.add_factory(path, self.factory)
#         self.server.attach(None)
#         self.pipeline.set_state(Gst.State.PLAYING)

#     def run(self):
#         loop = GLib.MainLoop()
#         bus = self.pipeline.get_bus()
#         bus.add_signal_watch()
#         bus.connect("message", self.on_message, loop)
#         try:
#             loop.run()
#         except KeyboardInterrupt:
#             pass
#         finally:
#             self.pipeline.set_state(Gst.State.NULL)
#             self.server.stop()

#     def on_message(self, bus, message, loop):
#         mtype = message.type
#         if mtype == Gst.MessageType.EOS:
#             print("End of stream")
#             loop.quit()
#         elif mtype == Gst.MessageType.ERROR:
#             err, debug = message.parse_error()
#             print(f"Error: {err}, Debug: {debug}")
#             loop.quit()
#         elif mtype == Gst.MessageType.WARNING:
#             err, debug = message.parse_warning()
#             print(f"Warning: {err}, Debug: {debug}")
#         return True

# if __name__ == "__main__":
#     myfunction = MyFunction()
#     myfunction.start_pipeline()
#     server = GstServer(8554, "/test")
#     server.run()


# # class MyFunction:
# #     def __init__(self):
# #         self.pipeline = None
# #         self.loop = GObject.MainLoop()

# #     def on_message(self, bus, message):
# #         t = message.type
# #         if t == Gst.MessageType.EOS:
# #             print("End of Stream")
# #             self.pipeline.set_state(Gst.State.NULL)
# #             self.loop.quit()class GstServer(GstRtspServer.RTSPServer):
#     def __init__(self, **properties):
#         super(GstServer, self).__init__(**properties)
#         self.factory = None
#         self.set_service(str(8554))
#         self.connect("client-connected", self.client_connected)

#     def set_factory(self, factory):
#         self.factory = factory

#     def client_connected(self, arg1, arg2):
#         print("Client connected")

# class MyFunction:
#     def __init__(self):
#         Gst.init(None)
#         self.pipeline = None
#         self.rtsp_server = None

#     def start_pipeline(self):
#         # self.rtsp_server = rtsp_server
#         self.pipeline = Gst.Pipeline()

#         source = Gst.ElementFactory.make("rtspsrc", "source")
#         source.set_property("location", "rtsp://admin:Rapidev321@192.168.23.166:554/")

#         depay = Gst.ElementFactory.make("rtph264depay", "depay")
#         decode = Gst.ElementFactory.make("decodebin", "decode")
#         convert = Gst.ElementFactory.make("videoconvert", "convert")
#         sink = Gst.ElementFactory.make("autovideosink", "sink")

#         self.pipeline.add(source)
#         self.pipeline.add(depay)
#         self.pipeline.add(decode)
#         self.pipeline.add(convert)
#         self.pipeline.add(sink)

#         source.link(depay)
#         depay.link(decode)
#         decode.link(convert)
#         convert.link(sink)

#         bus = self.pipeline.get_bus()
#         bus.add_signal_watch()
#         bus.connect("message::error", self.on_error)
#         bus.connect("message::state-changed", self.on_state_changed)

#         self.pipeline.set_state(Gst.State.PLAYING)

#     def on_state_changed(self, bus, message):
#         if message.src != self.pipeline:
#             return
#         old_state, new_state, pending_state = message.parse_state_changed()
#         print("Pipeline state changed from {} to {}".format(
#             Gst.Element.state_get_name(old_state), Gst.Element.state_get_name(new_state)))

#         if new_state == Gst.State.PLAYING:
#             print("Pipeline is now live")

#             # Add the pipeline to the RTSP server
#             factory = GstRtspServer.RTSPMediaFactory.new()
#             factory.set_element(self.pipeline)
#             factory.set_shared(True)
#             mount_points = self.get_mount_points()
#             mount_points.add_factory("/test", factory)
#             print("Pipeline string: {}".format(mount_points.get_mountpoint("/test").get_element().get_request_uri()))

#     def on_error(self, bus, message):
#         error, debug_info = message.parse_error()
#         print("Error received from element {}: {}".format(message.src.get_name(), error))
#         print("Debugging information: {}".format(debug_info))

#     def stop_pipeline(self):
#         if self.pipeline:
#             self.pipeline.set_state(Gst.State.NULL)
#             self.pipeline = None
#             print("Pipeline stopped")

# class GstServer:
#     def __init__(self, port, path):
#         self.pipeline = Gst.Pipeline()
#         self.server = GstRtspServer.RTSPServer()
#         self.server.set_service(str(port))
#         self.mounts = self.server.get_mount_points()
#         self.factory = GstRtspServer.RTSPMediaFactory()
#         self.factory.set_launch('( udpsrc port=5000 caps=application/x-rtp ! rtph264depay ! h264parse ! rtph264pay name=pay0 pt=96 )')
#         self.mounts.add_factory(path, self.factory)
#         self.server.attach(None)
#         self.pipeline.set_state(Gst.State.PLAYING)

#     def run(self):
#         loop = GLib.MainLoop()
#         bus = self.pipeline.get_bus()
#         bus.add_signal_watch()
#         bus.connect("message", self.on_message, loop)
#         try:
#             loop.run()
#         except KeyboardInterrupt:
#             pass
#         finally:
#             self.pipeline.set_state(Gst.State.NULL)
#             self.server.stop()

#     def on_message(self, bus, message, loop):
#         mtype = message.type
#         if mtype == Gst.MessageType.EOS:
#             print("End of stream")
#             loop.quit()
#         elif mtype == Gst.MessageType.ERROR:
#             err, debug = message.parse_error()
#             print(f"Error: {err}, Debug: {debug}")
#             loop.quit()
#         elif mtype == Gst.MessageType.WARNING:
#             err, debug = message.parse_warning()
#             print(f"Warning: {err}, Debug: {debug}")
#         return True

# if __name__ == "__main__":
#     myfunction = MyFunction()
#     myfunction.start_pipeline()
#     server = GstServer(8554, "/test")
#     server.run()



# class GstServer(GstRtspServer.RTSPServer):
#     def __init__(self, **properties):
#         super(GstServer, self).__init__(**properties)
#         self.factory = None
#         self.set_service(str(8554))
#         self.connect("client-connected", self.client_connected)

#     def set_factory(self, factory):
#         self.factory = factory

#     def client_connected(self, arg1, arg2):
#         print("Client connected")

# class MyFunction:
#     def __init__(self):
#         Gst.init(None)
#         self.pipeline = None
#         self.rtsp_server = None

#     def start_pipeline(self):
#         # self.rtsp_server = rtsp_server
#         self.pipeline = Gst.Pipeline()

#         source = Gst.ElementFactory.make("rtspsrc", "source")
#         source.set_property("location", "rtsp://admin:Rapidev321@192.168.23.166:554/")

#         depay = Gst.ElementFactory.make("rtph264depay", "depay")
#         decode = Gst.ElementFactory.make("decodebin", "decode")
#         convert = Gst.ElementFactory.make("videoconvert", "convert")
#         sink = Gst.ElementFactory.make("autovideosink", "sink")

#         self.pipeline.add(source)
#         self.pipeline.add(depay)
#         self.pipeline.add(decode)
#         self.pipeline.add(convert)
#         self.pipeline.add(sink)

#         source.link(depay)
#         depay.link(decode)
#         decode.link(convert)
#         convert.link(sink)

#         bus = self.pipeline.get_bus()
#         bus.add_signal_watch()
#         bus.connect("message::error", self.on_error)
#         bus.connect("message::state-changed", self.on_state_changed)

#         self.pipeline.set_state(Gst.State.PLAYING)

#     def on_state_changed(self, bus, message):
#         if message.src != self.pipeline:
#             return
#         old_state, new_state, pending_state = message.parse_state_changed()
#         print("Pipeline state changed from {} to {}".format(
#             Gst.Element.state_get_name(old_state), Gst.Element.state_get_name(new_state)))

#         if new_state == Gst.State.PLAYING:
#             print("Pipeline is now live")

#             # Add the pipeline to the RTSP server
#             factory = GstRtspServer.RTSPMediaFactory.new()
#             factory.set_element(self.pipeline)
#             factory.set_shared(True)
#             mount_points = self.get_mount_points()
#             mount_points.add_factory("/test", factory)
#             print("Pipeline string: {}".format(mount_points.get_mountpoint("/test").get_element().get_request_uri()))

#     def on_error(self, bus, message):
#         error, debug_info = message.parse_error()
#         print("Error received from element {}: {}".format(message.src.get_name(), error))
#         print("Debugging information: {}".format(debug_info))

#     def stop_pipeline(self):
#         if self.pipeline:
#             self.pipeline.set_state(Gst.State.NULL)
#             self.pipeline = None
#             print("Pipeline stopped")

# class GstServer:
#     def __init__(self, port, path):
#         self.pipeline = Gst.Pipeline()
#         self.server = GstRtspServer.RTSPServer()
#         self.server.set_service(str(port))
#         self.mounts = self.server.get_mount_points()
#         self.factory = GstRtspServer.RTSPMediaFactory()
#         self.factory.set_launch('( udpsrc port=5000 caps=application/x-rtp ! rtph264depay ! h264parse ! rtph264pay name=pay0 pt=96 )')
#         self.mounts.add_factory(path, self.factory)
#         self.server.attach(None)
#         self.pipeline.set_state(Gst.State.PLAYING)

#     def run(self):
#         loop = GLib.MainLoop()
#         bus = self.pipeline.get_bus()
#         bus.add_signal_watch()
#         bus.connect("message", self.on_message, loop)
#         try:
#             loop.run()
#         except KeyboardInterrupt:
#             pass
#         finally:
#             self.pipeline.set_state(Gst.State.NULL)
#             self.server.stop()

#     def on_message(self, bus, message, loop):
#         mtype = message.type
#         if mtype == Gst.MessageType.EOS:
#             print("End of stream")
#             loop.quit()
#         elif mtype == Gst.MessageType.ERROR:
#             err, debug = message.parse_error()
#             print(f"Error: {err}, Debug: {debug}")
#             loop.quit()
#         elif mtype == Gst.MessageType.WARNING:
#             err, debug = message.parse_warning()
#             print(f"Warning: {err}, Debug: {debug}")
#         return True

# if __name__ == "__main__":
#     myfunction = MyFunction()
#     myfunction.start_pipeline()
#     server = GstServer(8554, "/test")
#     server.run()


# # class MyFunction:
# #     def __init__(self):
# #         self.pipeline = None
# #         self.loop = GObject.MainLoop()

# #     def on_message(self, bus, message):
# #         t = message.type
# #         if t == Gst.MessageType.EOS:
# #             print("End of Stream")
# #             self.pipeline.set_state(Gst.State.NULL)
# #             self.loop.quit()class GstServer(GstRtspServer.RTSPServer):
#     def __init__(self, **properties):
#         super(GstServer, self).__init__(**properties)
#         self.factory = None
#         self.set_service(str(8554))
#         self.connect("client-connected", self.client_connected)

#     def set_factory(self, factory):
#         self.factory = factory

#     def client_connected(self, arg1, arg2):
#         print("Client connected")

# class MyFunction:
#     def __init__(self):
#         Gst.init(None)
#         self.pipeline = None
#         self.rtsp_server = None

#     def start_pipeline(self):
#         # self.rtsp_server = rtsp_server
#         self.pipeline = Gst.Pipeline()

#         source = Gst.ElementFactory.make("rtspsrc", "source")
#         source.set_property("location", "rtsp://admin:Rapidev321@192.168.23.166:554/")

#         depay = Gst.ElementFactory.make("rtph264depay", "depay")
#         decode = Gst.ElementFactory.make("decodebin", "decode")
#         convert = Gst.ElementFactory.make("videoconvert", "convert")
#         sink = Gst.ElementFactory.make("autovideosink", "sink")

#         self.pipeline.add(source)
#         self.pipeline.add(depay)
#         self.pipeline.add(decode)
#         self.pipeline.add(convert)
#         self.pipeline.add(sink)

#         source.link(depay)
#         depay.link(decode)
#         decode.link(convert)
#         convert.link(sink)

#         bus = self.pipeline.get_bus()
#         bus.add_signal_watch()
#         bus.connect("message::error", self.on_error)
#         bus.connect("message::state-changed", self.on_state_changed)

#         self.pipeline.set_state(Gst.State.PLAYING)

#     def on_state_changed(self, bus, message):
#         if message.src != self.pipeline:
#             return
#         old_state, new_state, pending_state = message.parse_state_changed()
#         print("Pipeline state changed from {} to {}".format(
#             Gst.Element.state_get_name(old_state), Gst.Element.state_get_name(new_state)))

#         if new_state == Gst.State.PLAYING:
#             print("Pipeline is now live")

#             # Add the pipeline to the RTSP server
#             factory = GstRtspServer.RTSPMediaFactory.new()
#             factory.set_element(self.pipeline)
#             factory.set_shared(True)
#             mount_points = self.get_mount_points()
#             mount_points.add_factory("/test", factory)
#             print("Pipeline string: {}".format(mount_points.get_mountpoint("/test").get_element().get_request_uri()))

#     def on_error(self, bus, message):
#         error, debug_info = message.parse_error()
#         print("Error received from element {}: {}".format(message.src.get_name(), error))
#         print("Debugging information: {}".format(debug_info))

#     def stop_pipeline(self):
#         if self.pipeline:
#             self.pipeline.set_state(Gst.State.NULL)
#             self.pipeline = None
#             print("Pipeline stopped")

# class GstServer:
#     def __init__(self, port, path):
#         self.pipeline = Gst.Pipeline()
#         self.server = GstRtspServer.RTSPServer()
#         self.server.set_service(str(port))
#         self.mounts = self.server.get_mount_points()
#         self.factory = GstRtspServer.RTSPMediaFactory()
#         self.factory.set_launch('( udpsrc port=5000 caps=application/x-rtp ! rtph264depay ! h264parse ! rtph264pay name=pay0 pt=96 )')
#         self.mounts.add_factory(path, self.factory)
#         self.server.attach(None)
#         self.pipeline.set_state(Gst.State.PLAYING)

#     def run(self):
#         loop = GLib.MainLoop()
#         bus = self.pipeline.get_bus()
#         bus.add_signal_watch()
#         bus.connect("message", self.on_message, loop)
#         try:
#             loop.run()
#         except KeyboardInterrupt:
#             pass
#         finally:
#             self.pipeline.set_state(Gst.State.NULL)
#             self.server.stop()

#     def on_message(self, bus, message, loop):
#         mtype = message.type
#         if mtype == Gst.MessageType.EOS:
#             print("End of stream")
#             loop.quit()
#         elif mtype == Gst.MessageType.ERROR:
#             err, debug = message.parse_error()
#             print(f"Error: {err}, Debug: {debug}")
#             loop.quit()
#         elif mtype == Gst.MessageType.WARNING:
#             err, debug = message.parse_warning()
#             print(f"Warning: {err}, Debug: {debug}")
#         return True

# if __name__ == "__main__":
#     myfunction = MyFunction()
#     myfunction.start_pipeline()
#     server = GstServer(8554, "/test")
#     server.run()


# # class MyFunction:
# #     def __init__(self):
# #         self.pipeline = None
# #         self.loop = GObject.MainLoop()

# #     def on_message(self, bus, message):
# #         t = message.type
# #         if t == Gst.MessageType.EOS:
# #             print("End of Stream")
# #             self.pipeline.set_state(Gst.State.NULL)
# #             self.loop.quit()
# #         elif t == Gst.MessageType.ERROR:
# #             err, debug = message.parse_error()
# #             print("Error: ", err, debug)
# #             self.pipeline.set_state(Gst.State.NULL)
# #             self.loop.quit()

# #     def start(self):
#         # Create pipeline
#         self.pipeline = Gst.parse_launch(
#             "rtspsrc location='rtsp://admin:Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0' ! rtph264depay ! h264parse ! decodebin ! autovideosink"
#         )

#         # Set up bus to get messages
#         bus = self.pipeline.get_bus()
#         bus.add_signal_watch()
#         bus.connect("message", self.on_message)

#         # Start pipeline
#         self.pipeline.set_state(Gst.State.PLAYING)
#         self.loop.run()


# class GstServer:
#     def __init__(self, pipeline_string):
#         self.pipeline_string = pipeline_string

#     def run(self):
#         Gst.init(None)

#         # Create pipeline
#         pipeline = Gst.parse_launch(self.pipeline_string)

#         # Start RTSP server
#         rtsp_server = pipeline.get_by_name("rtsp-server")
#         rtsp_server.set_state(Gst.State.PLAYING)

#         # Start pipeline
#         pipeline.set_state(Gst.State.PLAYING)

#         # Run main loop
#         loop = GObject.MainLoop()
#         try:
#             loop.run()
#         except KeyboardInterrupt:
#             pass

#         # Stop pipeline and RTSP server
#         pipeline.set_state(Gst.State.NULL)
#         rtsp_server.set_state(Gst.State.NULL)

# if __name__ == "__main__":
#     # Start MyFunction to read RTSP camera stream
#     my_function = MyFunction()
#     my_function.start()

#     # Get pipeline string from MyFunction and start RTSP server
#     pipeline_string = my_function.pipeline_string
#     rtsp_server = GstServer(pipeline_string)
#     rtsp_server.run()