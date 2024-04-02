import torch.backends.cudnn as cudnn
from PIL import Image
import cv2, os, random, torch, uuid, numpy as np, io, base64, logging
from models.experimental import attempt_load
from utils.general import check_img_size, non_max_suppression, set_logging, scale_coords
from utils.torch_utils import select_device, load_classifier, TracedModel
from utils.plots import plot_one_box
from ftp_connection import Ftp_Stream

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



class Model:
    agnostic_nms = False
    augment=False
    classes = None
    conf_thres=0.76
    device = '' #0, 1, 2, 3 for gpu ------ for cpu empty string or 'cpu'
    exist_ok = False
    img_size = 640
    iou_thres = 0.45
    name = 'exp'
    no_trace = False
    nosave = False
    project = 'runs/detect'
    save_conf=False
    save_txt=False
    update=False
    view_img=False
    weights=['best.pt']
    model=''
    stride = ''
    imgsz = ''
    half = ''

    def __init__(self, device = '', #0, 1, 2, 3 for gpu ------ for cpu empty string or 'cpu'
                 img_size = 640, no_trace = False, save_txt=False, view_img=False,    weights=['best.pt']):
        
        # FTP Connection
        try:            
            self.ftp_class = Ftp_Stream()
            self.ftp_cursor = self.ftp_class.getFTP()
            self.base_url = self.ftp_class.getBaseURL()
            logger.info("FTP Connection Established")
        except Exception as e:
            logger.info("Failed to establish connection with FTP")
        
        

        weights, view_img, save_txt, self.imgsz, trace = weights, view_img, save_txt, img_size, not no_trace

        # Initialize
        set_logging()
        self.device = select_device(device)
        self.half = self.device.type != 'cpu'  # half precision only supported on CUDA

        # Load model
        try:
            self.model = attempt_load(weights, map_location=self.device)  # load FP32 model
            logger.info("Moadel Loaded Successfully")
        except:
            logger.info("Failed to load model")

        self.stride = int(self.model.stride.max())  # model stride
        self.imgsz = check_img_size(self.imgsz, s=self.stride)  # check img_size

        if trace:
            self.model = TracedModel(self.model, self.device, img_size)

        if self.half:
            self.model.half()  # to FP16

         # Run inference
        if self.device.type != 'cpu':
            self.model(torch.zeros(1, 3, self.imgsz, self.imgsz).to(self.device).type_as(next(self.model.parameters())))  # run once

        # Get names and colors
        self.names = self.model.module.names if hasattr(self.model, 'module') else self.model.names
        self.colors = [[random.randint(0, 255) for _ in range(3)] for _ in self.names]

    def getModel(self):
        return self.model
        
    def create_request_args(self, frame):
        image = cv2.imencode('.jpg', frame)[1].tobytes()
        return image


    def letterbox(self, img, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True, stride=32):
        # Resize and pad image while meeting stride-multiple constraints
        shape = img.shape[:2]  # current shape [height, width]
        if isinstance(new_shape, int):
            new_shape = (new_shape, new_shape)

        # Scale ratio (new / old)
        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
        if not scaleup:  # only scale down, do not scale up (for better test mAP)
            r = min(r, 1.0)

        # Compute padding
        ratio = r, r  # width, height ratios
        new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
        if auto:  # minimum rectangle
            dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding
        elif scaleFill:  # stretch
            dw, dh = 0.0, 0.0
            new_unpad = (new_shape[1], new_shape[0])
            ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # width, height ratios

        dw /= 2  # divide padding into 2 sides
        dh /= 2

        if shape[::-1] != new_unpad:  # resize
            img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
        return img, ratio, (dw, dh)

    def convert_2d_to_3d(self, image):
        image.save('current.png')
        img = cv2.imread('current.png')
        os.remove('current.png')
        return img

    def transform(self, image_bytes):
        img = Image.open(image_bytes)
        arr = np.float32(img)
        image_shape = arr.shape

        if len(image_shape)<3:
            img = self.convert_2d_to_3d(img)
            arr = np.float32(img)
            image_shape = arr.shape

        return arr


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
            # logger.error("something went wrong... Reason: {}".format(E))
            return False


    
    def detect(self, source, im0s, video):
        # Second-stage classifier
        classify = False
        if classify:
            modelc = load_classifier(name='resnet101', n=2)  # initialize
            modelc.load_state_dict(torch.load('weights/resnet101.pt', map_location=self.device)['model']).to(self.device).eval()

        # dataset=source

        # Get names and colors
        names = self.model.module.names if hasattr(self.model, 'module') else self.model.names
        colors = [[random.randint(0, 255) for _ in range(3)] for _ in names]

        old_img_w = old_img_h = self.imgsz
        old_img_b = 1

        # for img in dataset:
        img = source
        img = torch.from_numpy(img).to(self.device)
        img = img.half() if self.half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        
        if img.ndimension() == 3:
            img = img.unsqueeze(0)
        # Warmup
        if self.device.type != 'cpu' and (old_img_b != img.shape[0] or old_img_h != img.shape[2] or old_img_w != img.shape[3]):
            old_img_b = img.shape[0]
            old_img_h = img.shape[2]
            old_img_w = img.shape[3]
            for i in range(3):
                self.model(img, augment=self.augment)[0]

        # Inference
        with torch.no_grad():
            pred = self.model(img, augment=self.augment)[0]
        torch.cuda.empty_cache()
        logger.info("Inference Success")

        # Apply NMS
        pred = non_max_suppression(pred, self.conf_thres, self.iou_thres, classes=self.classes, agnostic=self.agnostic_nms)

        # Process detections
        for i, det in enumerate(pred):  # detections per image
            im0 = im0s
            if im0.shape[0]>700:
                thickness = 3
            elif im0.shape[0]<700 & im0.shape[0]>400:
                thickness = 2
            elif im0.shape[0]<400:
                thickness = 1
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                # Plot Resutls on image
                for *xyxy, conf, cls in reversed(det):
                    label = f'{names[int(cls)]} {conf:.2f}'
                    plot_one_box(xyxy, im0, label=label, color=colors[int(cls)], line_thickness=thickness)
        logger.info("Plotting Done")
        if video: #if the comming image is a frame from a video
            im0 = self.create_request_args(im0)
            im0 = base64.b64encode(im0)
            return pred, im0

        else: #if it is image

            try:
                file_name = str(uuid.uuid4())+'.jpeg'
                image_link = self.imageToFTP('/AIX/Frames/', file_name, im0)
                logger.info("Image stored to FTP")
            except Exception as e:
                print("FTP ERRORL: "+ str(e))

            return pred, image_link


    
    def detect_live(self, source, im0s): #source is preprocessed image and im0s is original coming image
        
        old_img_w = old_img_h = self.imgsz
        old_img_b = 1

        img = source
        img = torch.from_numpy(img).to(self.device)
        img = img.half() if self.half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        
        if img.ndimension() == 3:
            img = img.unsqueeze(0)
        # Warmup
        if self.device.type != 'cpu' and (old_img_b != img.shape[0] or old_img_h != img.shape[2] or old_img_w != img.shape[3]):
            old_img_b = img.shape[0]
            old_img_h = img.shape[2]
            old_img_w = img.shape[3]
            for i in range(3):
                self.model(img, augment=self.augment)[0]

        # Inference
        with torch.no_grad():
            pred = self.model(img, augment=self.augment)[0]
        torch.cuda.empty_cache()
        # logger.info("Inference Success")

        # Apply NMS
        pred = non_max_suppression(pred, self.conf_thres, self.iou_thres, classes=self.classes, agnostic=self.agnostic_nms)

        # Process detections
        for i, det in enumerate(pred):  # detections per image
            im0 = im0s
            if im0.shape[0]>700:
                thickness = 3
            elif im0.shape[0]<700 & im0.shape[0]>400:
                thickness = 2
            elif im0.shape[0]<400:
                thickness = 1
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                # Plot Resutls on image
                for *xyxy, conf, cls in reversed(det):
                    label = f'{self.names[int(cls)]} {conf:.2f}'
                    plot_one_box(xyxy, im0, label=label, color=self.colors[int(cls)], line_thickness=thickness)
                
                return pred, im0
