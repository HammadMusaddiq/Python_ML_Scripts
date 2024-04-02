from PIL import Image
import io, numpy as np, requests, logging, cv2, random, uuid, os
from ultralytics import YOLO
from ftp_connection import Ftp_Stream
from dotenv import load_dotenv

load_dotenv()

# Logging Intialization
logger = logging.getLogger(__name__) 
if logger.hasHandlers():
    logger.handlers.clear()

formatter = logging.Formatter('%(asctime)s | %(name)s |  %(levelname)s | %(message)s') 
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('app.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

class MODEL:

    weights_path = os.getenv('MODEL_PATH')
    Model = ''

    def __init__(self):
        
        #Loading the model
        try:
            self.Model = YOLO(self.weights_path)
            logger.info("Model Loaded Successfully")
        except Exception as e:
            logger.errot(f"Error Loading the model {e}")
        
        #FTP Connection
        try:          
            self.ftp_class = Ftp_Stream()
            self.ftp_cursor = self.ftp_class.getFTP()
            self.base_url = self.ftp_class.getBaseURL()
            logger.info("FTP Connection Established")
        except Exception as e:
            logger.info("Failed to establish connection with FTP")

    def getModel(self):
        return self.Model

    def create_request_args(self, frame):
        image = cv2.imencode('.jpg', frame)[1].tobytes()
        return image
    
    def predict(self, source):
        result = self.Model.predict(source)
        return result
    
    def create_request_args(self, frame):
        image = cv2.imencode('.jpg', frame)[1].tobytes()
        return image
    
    def plot_one_box(self, x, img, label, line_thickness=3):
        # Plots one bounding box on image img
        tl = line_thickness or round(0.002 * (img.shape[0] + img.shape[1]) / 2) + 1  # line/font thickness
        color = [random.randint(0, 255) for _ in range(3)]
        c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))
        cv2.rectangle(img, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
        if label:
            tf = max(tl - 1, 1)  # font thickness
            t_size = cv2.getTextSize(label, 0, fontScale=tl / 3, thickness=tf)[0]
            c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
            cv2.rectangle(img, c1, c2, color, -1, cv2.LINE_AA)  # filled
            cv2.putText(img, label, (c1[0], c1[1] - 2), 0, tl / 3, [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)
    
    def imageToFTP(self, path, file_name, image): #store image on FTP
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        image_array = Image.fromarray(np.uint8(image))
        image_bytes = io.BytesIO() 
        image_array.save(image_bytes, format="jpeg") 
        image_bytes.seek(0)

        # logger.info('Uploading Image to FTP')
        if not self.ftp_class.is_connected():
            self.ftp_class.retry_ftp_connection()
            self.ftp_class.change_ftp_present_working_dir(path)
        else:
            self.ftp_class.change_ftp_present_working_dir(path)
        
        try:
            baseurl = self.base_url # ('str' object has no attribute 'copy')
            # for p in path.split('/'):
            #     baseurl = baseurl + str(p) + '/'
            baseurl = baseurl + path
            ftp_file_url = baseurl + file_name
            self.ftp_cursor.storbinary("STOR " + file_name , image_bytes)
            # ftp_cursor.quit()
            
            # logger.info("Image saved on Ftp URL: "+str(ftp_file_url))
            return ftp_file_url

        except Exception as E:
            logger.error("something went wrong... Reason: {}".format(E))
            return False
        
    def store_image_on_ftp(self, ploted_image):
        try:
            file_name = str(uuid.uuid4())+'.jpeg'
            image_link = self.imageToFTP('/AIX/Frames', file_name, ploted_image)
            image_link = image_link.replace(file_name, '/'+file_name)
            logger.info("Image stored to FTP")
        except Exception as e:
            print("FTP ERRORL: "+ str(e))
        return image_link