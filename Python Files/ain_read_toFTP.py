from datetime import datetime
import json
from kafka import KafkaProducer
import cv2
from datetime import datetime
import uuid
from PIL import Image
from PIL import ExifTags as TAGS
from ftp_download import Ftp_Save


camera_topic="camera-1"

def json_serializer(data):
    return json.dumps(data).encode()

def send_data(data):
    producer = KafkaProducer(bootstrap_servers=['10.100.150.100:9092'], 
    value_serializer=json_serializer,
    max_request_size=10485880)
    producer.send(camera_topic, data)



camera_ip = '192.168.23.199'
camera_user = 'admin'
camera_pass ='Admin12345'
ftp_save=Ftp_Save()

live_feed = "rtsp://"+camera_user+":"+camera_pass+"@"+camera_ip  # CCTV Camera
vid = cv2.VideoCapture(live_feed, cv2.CAP_FFMPEG)
count=0

start=datetime.now()
frame_count=0
while vid.isOpened():   
    ret, frame = vid.read()
    current_time = datetime.now()
    c_time = current_time.strftime("%d/%m/%Y %H:%M:%S")
    count+=1
    # if frame is read correctly ret is True
    if not ret:
        pass
            
    else:
        if count%3==0:
            frame_count+=1
            if frame_count%3==0:
                print('Frames Done :: ',frame_count)
                end=datetime.now()
                print('Time Taken for 3 frames :: ',end-start)  
                start=datetime.now()

            

            # dim = (900, 1200)
            # img = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)       
            # imdata = pickle.dumps(img)
            # import pdb;pdb.set_trace()
            
            kafka_id=str(uuid.uuid4())
            
            file_name=kafka_id+'.jpg'
            cvt_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            image_link = ftp_save.imageToFTP("/AIN/Frames/Images", file_name, cvt_frame,frame_count)

            # imdata = pickle.dumps(frame)
            # img = base64.b64encode(imdata).decode('ascii')
            test = {
                "camera_ip":camera_ip,
                "kafka_id":kafka_id,
                "time":c_time,
                "image" : image_link
                }
            send_data(test)            




        # # Naming a window
        # cv2.namedWindow("Resized_Window", cv2.WINDOW_NORMAL)

        # # Using resizeWindow()
        # cv2.resizeWindow("Resized_Window", 1400, 800) # (w,h)

        # # Displaying the image
        # cv2.imshow("Resized_Window", frame)
        
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

vid.release()
# cv2.destroyAllWindows() ## To destroy All shown frames
  
