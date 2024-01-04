import cv2, gi

#Gi Streamer
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GObject, GLib


class SensorFactory(GstRtspServer.RTSPMediaFactory):

    # model=''
    fps = 20
    image_width = 1280
    image_height = 720
    counter = 0

    def __init__(self, **properties):

        #Url for live stream
        # self.source = "rtsp://admin:Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0"
        # self.source = "rtsp://admin:Rapidev@321@192.168.23.166:554"
        self.source = "rtsp://admin:Rapidev321@192.168.23.166:554/cam/realmonitor?channel=1&subtype=0"
        
        #GStreamer Initialization
        super(SensorFactory, self).__init__(**properties)
        self.cap = cv2.VideoCapture(self.source)#ret, frame = video.read()
        self.number_frames = 0
        # self.fps = self.fps
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS)/2)
        print(self.fps)
        # ret, self.frame = self.cap.read()
        # self.width = self.frame.shape[1]
        # self.height = self.frame.shape[0]

        self.width = 2560
        self.height = 1440

        self.duration = 1 / self.fps * Gst.SECOND  # duration of a frame in nanoseconds
        # self.launch_string = 'appsrc name=source is-live=true block=true format=GST_FORMAT_TIME ' \
        #                      'caps=video/x-raw,format=BGR,width={},height={},framerate={}/1 ' \
        #                      '! videoconvert ! video/x-raw,format=I420 ' \
        #                      '! x264enc speed-preset=ultrafast tune=zerolatency ' \
        #                      '! rtph264pay config-interval=1 name=pay0 pt=96' \
        #                      .format(self.image_width, self.image_height, self.fps)
        
        self.launch_string = 'appsrc name=source is-live=true block=true format=GST_FORMAT_TIME ' \
                             'caps=video/x-raw,format=BGR,width={},height={},framerate={}/1 ' \
                             '! videoconvert ' \
                             '! video/x-raw,format=I420 ' \
                             '! x264enc speed-preset=ultrafast tune=zerolatency ' \
                             '! rtph264pay config-interval=1 name=pay0 pt=96' \
                             .format(self.width, self.height, self.fps)
        
        # self.launch_string = 'appsrc name=source is-live=true block=true format=GST_FORMAT_TIME ' \
        #                      'caps=video/x-raw,format=BGR,width={},height={},framerate={}/1 ' \
        #                      '! videoconvert ' \
        #                      '! video/x-raw,format=I420 ' \
        #                      '! x264enc speed-preset=ultrafast tune=zerolatency ' \
        #                      '! rtph264pay config-interval=1 name=pay0 pt=96 ' \
        #                      .format(self.width, self.height, self.fps)

        print('gst-launch-1.0', self.launch_string)
    
    #Live streaming and detection
    def on_need_data(self, src, length):
        
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # print(frame.shape)
                # img0 = frame  # BGR
                # # Padded resize
                # img = non_sattelite_model.letterbox(img0, non_sattelite_model.img_size, stride=non_sattelite_model.stride)[0]
                # # Convert
                # img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
                # img = np.ascontiguousarray(img)
                # source = img #np.expand_dims(frame, 0)

                # data = frame
                data = frame.tobytes()
                buf = Gst.Buffer.new_allocate(None, len(data), None)
                buf.fill(0, data)
                buf.duration = self.duration
                timestamp = self.number_frames * self.duration
                buf.pts = buf.dts = int(timestamp)
                buf.offset = timestamp
                self.counter += 1
                self.number_frames += 1
                retval = src.emit('push-buffer', buf)
                print('pushed buffer, frame {}, duration {} ns, durations {} s'.format(self.number_frames,
                                                                                       self.duration,
                                                                                       self.duration / Gst.SECOND))
                if retval != Gst.FlowReturn.OK:
                    print(retval)

    # attach the launch string to the override method
    def do_create_element(self, url):
        return Gst.parse_launch(self.launch_string)
    
    # attaching the source element to the rtsp media
    def do_configure(self, rtsp_media):
        self.number_frames = 0
        appsrc = rtsp_media.get_element().get_child_by_name('source')
        appsrc.connect('need-data', self.on_need_data)


# Rtsp server implementation where we attach the factory sensor with the stream uri
class GstServer(GstRtspServer.RTSPServer):
    port = 8556
    stream_uri = "/video_stream"

    def __init__(self, **properties):
        super(GstServer, self).__init__(**properties)
        self.factory = SensorFactory()
        self.factory.set_shared(True)
        self.set_service(str(self.port)) # if port added then comment this line
        self.get_mount_points().add_factory(self.stream_uri, self.factory)
        self.attach(None)

# initializing the threads and running the stream on loop.
# GObject.threads_init()
Gst.init(None)
server = GstServer()
# loop = GObject.MainLoop()
loop = GLib.MainLoop()
loop.run()