# pip install PyGObject
# sudo apt-get install libgstrtspserver-1.0-dev gstreamer1.0-rtsp
# sudo apt-get install gstreamer1.0-plugins-ugly
# sudo apt-get install gstreamer1.0-plugins-bad
# sudo apt-get upgrade gstreamer1.0-plugins-good


import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib

# 1st method.
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
        self.server.get_mount_points().add_factory(self.mount_point, factory)
        self.server.attach(None)

        print("RTSP server started at rtsp://localhost:{}{}".format(self.port, self.mount_point))

    def stop(self):
        if self.server:
            self.server.detach()


# 2nd method.
class MyRTSPServer(GstRtspServer.RTSPServer):
    def __init__(self, server_ip, server_port, server_path, camera_ip, stream_url):
        super().__init__()

        # Create the GStreamer pipeline to generate the random video stream
        pipeline_str = 'videotestsrc ! video/x-raw,width=640,height=480 ! x264enc ! rtph264pay name=pay0 pt=96' # for random data
        # pipeline_str = f"rtspsrc location='rtsp://{camera_ip}/{stream_url}' latency=0 ! rtph264depay ! h264parse ! rtph264pay name=pay0 pt=96"
        # pipeline_str = f"uridecodebin uri='rtsp://{camera_ip}/{stream_url}' ! videoconvert ! x264enc ! rtph264pay name=pay0 pt=96"
        print("gst-launch-1.0", pipeline_str)

        server = GstRtspServer.RTSPServer.new()
        server.props.service = "%d" % server_port
        server.attach(None)

        factory = GstRtspServer.RTSPMediaFactory.new()
        factory.set_launch(pipeline_str)
        factory.set_shared(True)
        server.get_mount_points().add_factory(server_path, factory)



if __name__ == '__main__':
    server = RTSPServer(8556, "/test")
    server.start()

    # new_server = MyRTSPServer(server_ip='192.168.18.229', server_port=8556, server_path='/stream', camera_ip='admin:Rapidev321@192.168.23.166:554' , stream_url='cam/realmonitor?channel=1&subtype=0')


    loop = GLib.MainLoop()
    loop.run()





# RTSP RUNNING
# gst-launch-1.0 rtspsrc location='rtsp://admin:Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0' ! rtph264depay ! h264parse ! splitmuxsink location=file%02d.mp4 max-size-time=10000000000 

# RTSP OUT
# gst-launch-1.0 -v videotestsrc ! x264enc ! rtph264pay pt=96 ! udpsink host=192.168.18.229 port=8556
# gst-launch-1.0 -v videotestsrc  ! videoconvert ! autovideosink

# gst-launch-1.0 rtspsrc location='rtsp://admin:Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0' ! decodebin ! x264enc tune=zerolatency ! rtph264pay name=pay0 pt=96 
# gst-launch-1.0 rtspsrc location='rtsp://admin:Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0' ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink port=5005

# gst-launch-1.0 rtspsrc location='rtsp://admin:Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0' ! decodebin ! x264enc tune=zerolatency ! rtph264pay name=pay0 pt=96 ! tcpserversink host=192.168.18.229 port=5005 location=/stream
# gst-launch-1.0 rtspsrc location='rtsp://admin:Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0' ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! tee name=t ! queue ! autovideosink t. ! queue ! mux. ! matroskamux name=mux ! tcpserversink host=192.168.18.229 port=5005 location=/stream

# gst-launch-1.0 rtspsrc location='rtsp://admin:Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0' ! x264enc ! rtph264pay pt=96 ! udpsink host=192.168.18.229 port=5005 location=/stream
# gst-launch-1.0 -v videotestsrc ! x264enc ! rtph264pay pt=96 ! udpsink host=192.168.0.10 port=5000

# gst-launch-1.0 rtspsrc location='rtsp://admin:Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0' latency=0 ! rtph264depay ! h264parse ! rtph264pay name=pay0 pt=96 ! udpsink host=192.168.18.229 port=5005 sync=false async=false
# gst-launch-1.0 rtspsrc location='rtsp://admin:Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0' latency=0 ! rtph264depay ! h264parse ! rtph264pay name=pay0 pt=96 ! udpsink host=192.168.18.229 port=5005 sync=false async=false | gst-rtsp-server -v --gst-debug-level=3 -m -p 5006 /stream
# gst-launch-1.0 rtspsrc location='rtsp://admin:Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0' latency=0 ! rtph264depay ! h264parse ! rtph264pay name=pay0 pt=96 ! udpsink host=192.168.18.229 port=5005 sync=false async=false


# gst-launch-1.0 rtspsrc location='rtsp://admin:Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0' latency=0 ! rtph264depay ! h264parse ! rtph264pay name=pay0 pt=96 ! udpsink host=192.168.23.199 port=5005 sync=false async=false | gst-rtsp-server -v --gst-debug-level=3 -m -p 5006 /stream
# gst-launch-1.0 rtspsrc location='rtsp://admin:Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0' latency=10 ! rtph264depay ! h264parse ! decodebin ! autovideosink

# gst-launch-1.0 videotestsrc ! video/x-raw,width=640,height=480 ! x264enc ! rtph264pay name=pay0 pt=96 
# gst-launch-1.0 videotestsrc ! video/x-raw,width=640,height=480 ! x264enc ! rtph264pay name=pay0 pt=96 ! decodebin ! autovideosink

# gst-launch-1.0 rtspsrc location='rtsp://admin:Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0' latency=0 ! rtph264depay ! h264parse ! rtph264pay name=pay0 pt=96 ! udpsink host=192.168.23.199 port=5005 

# pipeline_str = f"rtspsrc location='rtsp://{camera_ip}/{stream_url}' latency=0 ! rtph264depay ! h264parse ! rtph264pay name=pay0 pt=96 ! queue ! udpsink host={server_ip} port={server_port}"
# pipeline_str = f'rtspsrc location=rtsp://{camera_ip}/{stream_url} latency=0 ! rtph264depay ! h264parse ! rtph264pay name=pay0 pt=96 ! queue'
        
# gst-launch-1.0 -v videotestsrc  ! videoconvert ! autovideosink
# gst-launch-1.0 videotestsrc ! video/x-raw,width=640,height=480 ! x264enc ! rtph264pay name=pay0 pt=96 ! decodebin ! autovideosink
# gst-launch-1.0 rtspsrc location='rtsp://admin:Rapidev321@192.168.23.166:554/cam/realmonitor?channel=1&subtype=0' latency=10 ! rtph264depay ! h264parse ! decodebin ! autovideosink
# gst-launch-1.0 playbin uri='rtsp://admin:Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0' video-sink=xvimagesink
# gst-launch-1.0 uridecodebin uri='rtsp://admin:Admin12345@192.168.23.199:554' ! videoconvert ! x264enc ! rtph264pay ! decodebin ! autovideosink
