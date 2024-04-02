import cv2, time, numpy as np, gi, json, logging
from datetime import datetime
from MODEL import Model
from kafka import KafkaProducer

#Gi Streamer
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GObject
from threading import Thread

#Logging Initialization
logger = logging.getLogger(__name__)
if logger.hasHandlers():
    logger.handlers.clear()

formatter = logging.Formatter('%(asctime)s | %(name)s |  %(levelname)s | %(message)s')
logger.setLevel("DEBUG")

file_handler = logging.FileHandler("Live_Stream.log")
file_handler.setFormatter(formatter)
file_handler.setLevel("DEBUG")
logger.addHandler(file_handler)


try:
    non_sattelite_model = Model()
    logger.info("Starting Live Streaming, Model Initialized")
except Exception as e:
    logger.info("Model Not initialized", e)

class SensorFactory(GstRtspServer.RTSPMediaFactory):

    # model=''
    fps = 20
    image_width = 1280
    image_height = 720
    port = 8554
    stream_uri = "/video_stream"
    counter = 0
    f_p_s = 25

    def __init__(self, **properties):

        self.f_p_s = 25
        #Intialize Kafka
        self.mulhim_kafka = ["10.100.160.100:9092"]
        self.topic = "live-stream-data"
        #Url for live stream
        url = 'rtsp://admin:Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0'
        self.source = url
        #GStreamer Initialization
        super(SensorFactory, self).__init__(**properties)
        self.cap = cv2.VideoCapture(self.source)
        self.number_frames = 0
        self.fps = self.fps
        self.duration = 1 / self.fps * Gst.SECOND  # duration of a frame in nanoseconds
        self.launch_string = 'appsrc name=source is-live=true block=true format=GST_FORMAT_TIME ' \
                             'caps=video/x-raw,format=BGR,width={},height={},framerate={}/1 ' \
                             '! videoconvert ! video/x-raw,format=I420 ' \
                             '! x264enc speed-preset=ultrafast tune=zerolatency ' \
                             '! rtph264pay config-interval=1 name=pay0 pt=96' \
                             .format(self.image_width, self.image_height, self.fps)

    def json_serializer(self, data):
        return json.dumps(data).encode()

    def send_data(self, topic, data):
        """Function to Send Data in Kafka Topic"""
        producer = KafkaProducer(
            bootstrap_servers=self.mulhim_kafka,
            value_serializer=self.json_serializer,
        )
        producer.send(topic, data)

    def create_preds_out(self, pred):
        labels = ['Civilian_Vehicle', 'Grenade', 'Gun', 'Military_Tank', 'Military_Vehicle', 'Person', 'Pistol', 'Soldier']
        predictions = pred
        con = []
        bbox = []
        label = []
        if len(predictions) > 0:
            for each in predictions:
                con.append(float(each[4])*100)
                bbox.append(each[:4].cpu().detach().numpy())
                label.append(labels[int(each[5])])
        object_count = {}
        for L in labels:
            object_count[L] = label.count(L)
        data = {'confidence':con,
                # 'bbox':bbox,
                'label':label,
                'object_count': object_count,
                'timestamp':str(datetime.now())}
        self.send_data(self.topic, data)
        
    #Live streaming and detection
    def on_need_data(self, src, length):
        
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                img0 = frame  # BGR
                # Padded resize
                img = non_sattelite_model.letterbox(img0, non_sattelite_model.img_size, stride=non_sattelite_model.stride)[0]
                # Convert
                img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
                img = np.ascontiguousarray(img)
                source = img #np.expand_dims(frame, 0)
                try:
                    preds, frame = non_sattelite_model.detect_live(source, img0)
                except Exception as e:
                    logger.info("Exception in inference", e)
                if self.counter == self.f_p_s:
                    try:
                        Thread(target=self.create_preds_out, args=preds,).start()
                    except Exception as e:
                        logger.info("Exception in Kafka Producer, Not able to send data", e)
                    self.counter = 0
                
                data = frame.tostring()
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
    fps = 15
    image_width = 640
    image_height = 640
    port = 8554
    stream_uri = "/video_stream"

    def __init__(self, **properties):
        super(GstServer, self).__init__(**properties)
        self.factory = SensorFactory()
        self.factory.set_shared(True)
        self.set_service(str(self.port))
        self.get_mount_points().add_factory(self.stream_uri, self.factory)
        self.attach(None)

# initializing the threads and running the stream on loop.
GObject.threads_init()
Gst.init(None)
server = GstServer()
loop = GObject.MainLoop()
loop.run()