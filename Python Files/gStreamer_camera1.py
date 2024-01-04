# pip install PyGObject
# sudo apt-get install libgstrtspserver-1.0-dev gstreamer1.0-rtsp
# sudo apt-get install gstreamer1.0-plugins-ugly
# sudo apt-get install gstreamer1.0-plugins-bad
# sudo apt-get upgrade gstreamer1.0-plugins-good



# import gi
# gi.require_version('Gst', '1.0')
# from gi.repository import Gst
# Gst.init(None)

# pipeline = Gst.Pipeline()
# # src = Gst.ElementFactory.make('v4l2src', 'camera-source')
# src = Gst.ElementFactory.make('uridecodebin', 'camera-source')
# vidconvert = Gst.ElementFactory.make('videoconvert', 'converter')
# vidsink = Gst.ElementFactory.make('ximagesink', 'videosink')

# pipeline.add(src)
# pipeline.add(vidconvert)
# pipeline.add(vidsink)
# src.link(vidconvert)
# vidconvert.link(vidsink)

# # src.set_property('uri', 'rtsp://admin:Rapidev@321@192.168.23.166:554')
# src.set_property('uri', 'rtsp://admin:Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0')
# pipeline.set_state(Gst.State.PLAYING)

# bus = pipeline.get_bus()

# msg = bus.timed_pop_filtered(Gst.CLOCK_TIME_NONE, Gst.MessageType.ERROR | Gst.MessageType.STATE_CHANGED)
# import pdb; pdb.set_trace()
# print("")

# while True:
#     msg = bus.poll(Gst.MessageType.ANY, Gst.CLOCK_TIME_NONE)

#     if msg is None:
#         continue

#     if msg.type == Gst.MessageType.ERROR:
#         err, debug = msg.parse_error()
#         print(f"Error received from element {msg.src.get_name()}: {err.message}")
#         print(f"Debugging information: {debug}")
#         break

#     if msg.type == Gst.MessageType.EOS:
#         print("End-Of-Stream reached.")
#         break

#     if msg.type == Gst.MessageType.STATE_CHANGED:
#         if msg.src == pipeline:
#             old_state, new_state, pending_state = msg.parse_state_changed()
#             print(f"Pipeline state changed from {old_state} to {new_state}")


# import gi
# gi.require_version('Gst', '1.0')
# gi.require_version('GstRtspServer', '1.0')
# from gi.repository import Gst, GstRtspServer
# Gst.init(None)

# class RtspServer(GstRtspServer.RTSPServer):
#     def __init__(self, **properties):
#         super(RtspServer, self).__init__(**properties)
#         self.factory = GstRtspServer.RTSPMediaFactory()
#         self.factory.set_shared(True)
#         self.factory.set_launch('( rtspsrc location=rtsp://admin:Rapidev@321@192.168.23.166:554 ! decodebin ! x264enc tune=zerolatency ! rtph264pay name=pay0 pt=96 )')

#         self.mount_points = self.get_mount_points()
#         self.mount_points.add_factory('/stream', self.factory)
#         self.attach(None)

# server = RtspServer()
# Gst.init(None)

# pipeline = Gst.parse_launch('( rtspsrc location=rtsp://admin:Rapidev@321@192.168.23.166:554 ! decodebin ! videoconvert ! queue ! x264enc tune=zerolatency ! rtph264pay name=pay0 pt=96 )')

# pipeline.set_state(Gst.State.PLAYING)

# while True:
#     pass


# import gi
# gi.require_version('Gst', '1.0')
# from gi.repository import GObject, Gst

# GObject.threads_init()
# Gst.init(None)

# pipeline_str = 'rtspsrc location=rtsp://admin:Rapidev@321@192.168.23.166:554 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink port=20005'

# pipeline = Gst.parse_launch(pipeline_str)
# pipeline.set_state(Gst.State.PLAYING)

# print("RTSP stream URL: ", pipeline_str)

# while True:
#     pass

# # bus = pipeline.get_bus()
# # msg = bus.timed_pop_filtered(Gst.CLOCK_TIME_NONE, Gst.MessageType.ERROR | Gst.MessageType.EOS)


# import gi
# gi.require_version('Gst', '1.0')
# from gi.repository import GObject, Gst

# GObject.threads_init()
# Gst.init(None)

# # rtsp_url = "rtsp://admin:Rapidev@321@192.168.23.166:554"
# rtsp_url = "rtsp://admin:Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0"
# http_port = "5015"
# http_path = "stream"

# pipeline_str = f'rtspsrc location={rtsp_url} ! decodebin ! x264enc tune=zerolatency ! rtph264pay name=pay0 pt=96 ! tcpserversink host=0.0.0.0 port={http_port} location=/{http_path}'
# # pipeline_str = f'rtspsrc location={rtsp_url} ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! tee name=t ! queue ! autovideosink t. ! queue ! mux. ! matroskamux name=mux ! tcpserversink host=0.0.0.0 port={http_port} location=/{http_path}'
# # pipeline_str = f'rtspsrc location={rtsp_url} ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! tee name=t ! queue ! autovideosink t. ! queue ! mux. ! matroskamux name=mux ! tcpserversink host=0.0.0.0 port={http_port} location=/{http_path}'

# print(pipeline_str)

# pipeline = Gst.parse_launch(pipeline_str)
# pipeline.set_state(Gst.State.PLAYING)

# print("HTTP stream URL: ", f"http://localhost:{http_port}/{http_path}")

# bus = pipeline.get_bus()
# msg = bus.timed_pop_filtered(Gst.CLOCK_TIME_NONE, Gst.MessageType.ERROR | Gst.MessageType.EOS)


import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject
Gst.init(None)

pipeline = Gst.Pipeline()

# Create RTSP source element
src = Gst.ElementFactory.make("rtspsrc", "source")
src.set_property("location", "rtsp://<username>:<password>@<rtsp-source-url>")
# src.set_property("latency", 0)
# src.set_property("drop-on-latency", True)

# Create RTP decoder element
# rtpdecoder = Gst.ElementFactory.make("rtph264depay", "rtpdecoder")

# Create H264 decoder element
# decoder = Gst.ElementFactory.make("avdec_h264", "decoder")

# Create video converter element
# videoconvert = Gst.ElementFactory.make("videoconvert", "videoconvert")

# Create video sink element for browser display
# videosink = Gst.ElementFactory.make("autovideosink", "videosink")
# videosink.set_property("sync", False)


# # Create video sink element for web server
# videosink = Gst.ElementFactory.make("filesink", "videosink")
# videosink.set_property("location", "http://localhost:5000/stream")


# # Create the RTSP source element
# source = Gst.ElementFactory.make("rtspsrc", "source")
# source.set_property("location", source_location)

# Create the RTSP sink element
sink = Gst.ElementFactory.make("rtspclientsink", "sink")
sink.set_property("location", "rtsp://localhost:5000/stream")


# Add elements to the pipeline
pipeline.add(src)
# pipeline.add(rtpdecoder)
# pipeline.add(decoder)
# pipeline.add(videoconvert)
pipeline.add(sink)

# Link elements together
src.link(sink)
# rtpdecoder.link(decoder)
# decoder.link(videoconvert)
# videoconvert.link(videosink)

# Start playing the pipeline
pipeline.set_state(Gst.State.PLAYING)

# Start the main loop and listen for events
mainloop = GObject.MainLoop()
mainloop.run()





