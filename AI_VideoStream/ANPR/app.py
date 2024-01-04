import json
import torch
import numpy as np
from PIL import Image
from flask import Flask, request
import cv2
import os
from models.experimental import attempt_load
from utils.general import check_img_size, non_max_suppression, set_logging
from utils.torch_utils import select_device, load_classifier, TracedModel
from npdetection.NPDetectionApp import NPDetection
import requests,io
import time
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
if (logger.hasHandlers()):
    logger.handlers.clear()

formatter = logging.Formatter('%(asctime)s | %(name)s |  %(levelname)s | %(message)s')
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("app.log")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

logger.info("App started")


app = Flask(__name__)



class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

class Inference(object):
    npModel = NPDetection()   
    exist_ok = False
    conf_thres = 0.5
    classes = None
    augment = False
    agnostic_nms = False
    iou_thres = 0.45
    name = 'exp'
    nosave = False
    project = 'runs/detect'
    save_conf = False
    update = False
    weights = ['yolov7_e6e.pt']
    view_img = False
    save_txt = False
    img_size = 640
    no_trace = False
    device = '' #0, 1, 2, 3 for gpu ------ for cpu empty string or 'cpu'

    def getNumDetModel(self):
        return self.npModel
        

    def parameters(self):
        device = self.device #0, 1, 2, 3 for gpu ------ for cpu empty string or 'cpu'
        no_trace = self.no_trace
        img_size = self.img_size
        weights = self.weights
        save_txt = self.save_txt
        view_img = self.view_img
        return weights, view_img, save_txt, img_size, no_trace, device

    def getlabels(self):
        labels = ['person','bicycle','car','motorbike','aeroplane','bus','train','truck','boat','traffic light','fire hydrant',
        'stop sign','parking meter','bench','bird','cat','dog','horse','sheep','cow','elephant','bear','zebra','giraffe','backpack',
        'umbrella','handbag','tie','suitcase','frisbee','skis','snowboard','sports ball','kite','baseball bat','baseball glove',
        'skateboard','surfboard','tennis racket','bottle','wine glass','cup','fork','knife','spoon','bowl','banana',
        'apple','sandwich','orange','broccoli','carrot','hot dog','pizza','donut','cake','chair','sofa','pottedplant','bed',
        'diningtable','toilet','tvmonitor','laptop','mouse','remote','keyboard','cell phone','microwave','oven','toaster',
        'sink','refrigerator','book','clock','vase','scissors','teddy bear','hair drier','toothbrush']
        return labels

    
          

    def detect(self, source):
        # Second-stage classifier
        classify = False
        if classify:
            modelc = load_classifier(name='resnet101', n=2)  # initialize
            modelc.load_state_dict(torch.load('weights/resnet101.pt', map_location=device)['model']).to(device).eval()

        dataset=[source]

        # Get names and colors
        names = model.module.names if hasattr(model, 'module') else model.names

        # Run inference
        if device.type != 'cpu':
            model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))  # run once
        old_img_w = old_img_h = imgsz
        old_img_b = 1

        for img in dataset:
            img = torch.from_numpy(img).to(device)
            img = img.half() if half else img.float()  # uint8 to fp16/32
            img /= 255.0  # 0 - 255 to 0.0 - 1.0
            
            if img.ndimension() == 3:
                img = img.unsqueeze(0)
            # img = img.permute(0, 3, 1, 2)
            # Warmup
            if device.type != 'cpu' and (old_img_b != img.shape[0] or old_img_h != img.shape[2] or old_img_w != img.shape[3]):
                old_img_b = img.shape[0]
                old_img_h = img.shape[2]
                old_img_w = img.shape[3]
                for i in range(3):
                    model(img, augment=self.augment)[0]

            # Inference
            pred = model(img, augment=self.augment)[0]

            # Apply NMS
            pred = non_max_suppression(pred, self.conf_thres, self.iou_thres, classes= self.classes, agnostic= self.agnostic_nms)

        return pred

    def convert_2d_to_3d(self, image):
        image.save('current.png')
        img = cv2.imread('current.png')
        os.remove('current.png')
        return img

    def transform(self, image_bytes):
        img = Image.open(image_bytes)
        #oriImg = img
        arr = np.uint8(img)
        oriImg = arr
        image_shape = arr.shape
        x, y, _ = arr.shape
        
        arr = cv2.resize(arr, (640, 640), interpolation=cv2.INTER_AREA)
        if len(image_shape)<3:
            img = self.convert_2d_to_3d(img)
            arr = np.uint8(img)
            image_shape = arr.shape

        # if image_shape[2] != 3: # convering image to 3 channels for extracting embeddings
        #     arr = arr[:,:,:3]
        return arr, oriImg

    
    def letterbox(self , img, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True, stride=32):
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
    
    def getCropImagesVehicle(self, data,frame):
        cropImages = []
        for key, value in data.items():
            if key == "bbox":
                for box in value:
                    X = int(box[0]) #x
                    Y = int(box[1]) #y
                    W = int(box[2]) #w 
                    H = int(box[3]) #h
                    #rec = frame.copy() #1
                    #rec = cv2.rectangle(rec, (X, Y), (W, H), (255,0,0), 4) #1
                    crop = frame.copy()
                    cropped_image = crop[Y:H, X:W]
                    # cv2.imshow('Croped', cropped_image)
                    # cv2.imshow('Frame', rec)
                    # cv2.waitKey(0)
                    # cv2.destroyAllWindows()
                    # cv2.imwrite("./frame str(uuid.uuid1())+".jpg",img12)    
                    cropImages.append(cropped_image)
        #cv2.imwrite("./saveFrame/ %s.jpg" % str(uuid.uuid1()), rec) # save frame as JPG file
        return cropImages
    
    
    
    
    def putlicencePlate(self, boxsssss,crop, label):
        # if label == []:
        #     label = "No Plate"
        rec = crop.copy()
        for box,label1 in zip(boxsssss,label):
            if label1 == []:
                label1 = "No Plate"
            
            X = int(box[0]) #x
            Y = int(box[1]) #y
            W = int(box[2]) #w 
            H = int(box[3]) #h
            rec = cv2.rectangle(rec, (X, Y), (W, H), (255,0,0), 4) #1
            labelled_image = cv2.putText(rec, label1, (X, Y-10), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 4)
        try: 
            os.mkdir("./saveFrame")
            os.mkdir("./saveFrame/saveVideo")
            cv2.imwrite("./saveFrame/ %s.jpg" % str(uuid.uuid1()), labelled_image) # save frame as JPG file
        except:
            cv2.imwrite("./saveFrame/ %s.jpg" % str(uuid.uuid1()), labelled_image) # save frame as JPG file
            
    def createVideo(self):
        print("Creating Video")
        image_folder = './saveFrame'
        # dir_list = [img for img in os.listdir(image_folder) if img.endswith(".jpg")]
        # # prints all files
        # print(dir_list)
        video_name = './saveFrame/saveVideo/filename.avi'
        
       
        frame_size = (720,720)
        #video_writer = cv2.VideoWriter(video_name,cv2.VideoWriter_fourcc(*'MJPG'),2, frame_size)

        images = [img for img in os.listdir(image_folder) if img.endswith(".jpg")]
        #images = images[0:10]

        frame = cv2.imread(os.path.join(image_folder, images[0]))

        height, width, _ = frame.shape
        video_writer = cv2.VideoWriter(video_name, 0, 2, (width,height))
        print(images)
        for image in images:
            video_writer.write(cv2.imread(os.path.join(image_folder, image)))
            
        cv2.destroyAllWindows()  
        video_writer.release()
    
    
    def set_annot(self, orig_image, boxes): #res_image_shape (width, height)
        true_boxes=[]
        o_w, o_h=orig_image.shape[0], orig_image.shape[1] #actual image width and height
        n_w, n_h = 640,640 #Yolo output image width and height
        for index, single_point in enumerate(boxes):
            if index%2==0:
                new_point = (o_h * single_point) / (n_h)
            else:
                new_point = (o_w * single_point) / (n_w)
            true_boxes.append(new_point)
        return true_boxes
    
    def getOrigBoxes(self, image_numpy,personBoxs): # get the orignal box according to orignal image
        newPersonBoxs = []
        #newVehicleBoxs = []
        for pbox in personBoxs:
            #print(pbox)
            newPBox = self.set_annot(image_numpy, pbox)
            newPersonBoxs.append(newPBox)
        # for vbox in vehicleBoxes:
        #     #print(vbox)
        #     newVBox = self.set_annot(image_numpy, vbox)
        #     newVehicleBoxs.append(newVBox)
        return newPersonBoxs
   
    def main(self):
        
        try:
            #pdb.set_trace()
            image = request.files['image_path']
            #print("Image Path recived",image)
            #frame = self.transform(image)
            frame, origImage = self.transform(image)
            frame=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            #print("Orignal shape",origImage.shape)
        except:
            try:
                nparr = np.fromstring(request.data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                origImage = frame
                frame = cv2.resize(frame, (640,640), cv2.INTER_AREA)
            except:
                link =request.form['image_path']
                response = requests.get(link)
                img = Image.open(io.BytesIO(response.content))
                arr = np.uint8(img)
                frame=cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)
                origImage = frame
                frame = cv2.resize(frame, (640,640), cv2.INTER_AREA)
        
        img0 = frame  # BGR
        img_size = self.img_size
        # Padded resize
        img = self.letterbox(img0, img_size, stride=stride)[0]
        # Convert
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        img = np.ascontiguousarray(img)
        source = img #np.expand_dims(frame, 0)
        

        # get the start time yolo
        yst = time.time()

        pred = self.detect(source)
        #get labels
        labels = self.getlabels()

        predictions = pred[0]


        # Vehicle data
        vehicleCon = []
        vehicleBbox = []
        vehicleLabel = []
        
        # person data
        #personCon = []
        personBbox = []
        #personLabel = []

        if len(predictions) > 0:
            for each1 in predictions:
                lab = labels[int(each1[5])]
                if lab == 'car' or lab == 'truck' or lab == 'bus' or lab == 'motorbike':
                    if ((each1[4])*100) > 80:          #confidence
                        vehicleCon.append(float(each1[4])*100)
                        vehicleBbox.append(each1[:4].cpu().detach().numpy())
                        vehicleLabel.append(labels[int(each1[5])])
                if lab == 'person':
                     if ((each1[4])*100) > 50:          #confidence
                        #vehicleCon.append(float(each1[4])*100)
                        personBbox.append(each1[:4].cpu().detach().numpy())
                        #vehicleLabel.append(labels[int(each1[5])])
            nPerson = len(personBbox)
            logger.info("Total found number of person are " + str(nPerson))
        else:
            logger.info("No predictions is found!")
        
        #get the orignal box of person according to orignal image
        if nPerson>0:
            personBoxs = self.getOrigBoxes(origImage,personBbox)
        else:
            personBoxs = 0
            logger.info("No person is found!")
            
        
            
        
        vehicleData = {'confidence':vehicleCon,
                'bbox':vehicleBbox,
                'label':vehicleLabel}

        personData = {'bbox':personBoxs,
        'peopleCount':nPerson}

        # time taken in retrieving car objects

        #print("Resize shape",frame.shape)
       
        
        # get the end time yolo
        yet = time.time()
        # get the execution time of yolo
        yelapsed_time = yet - yst
        print('----------------------------------- Execution time of YOLO7 to extract all vechicle objects:', yelapsed_time, 'seconds')


        # get the start time ANPR
        nst = time.time()
        license_text = []
        
        #getting crop image of car
        if len(vehicleBbox)>0:
            logger.info("Total found number of vehicle are " + str(len(vehicleBbox)))
            croppedImages = self.getCropImagesVehicle(vehicleData, frame)
            vehicleBboxs = self.getOrigBoxes(origImage,vehicleBbox)
            for _, crop_image in enumerate(croppedImages):
                #number plate detection
                licence_plate= self.getNumDetModel().plate_detection(crop_image)
                if(len(licence_plate)):
                    license_text.append(licence_plate)
                else:
                    license_text.append("No OCR")
            self.putlicencePlate(vehicleBboxs, origImage, license_text)
            
            #Creating Video
            self.createVideo()
        else:
            logger.info("No vehicle is found!")
        
        # # get the end time ANPR
        net = time.time()
        # # get the execution time of ANPR
        nelapsed_time = net - nst
        print('----------------------------------- Execution time of OCR process:', nelapsed_time, 'seconds')
        totalTime = nelapsed_time + yelapsed_time
        print('----------------------------------- Total Execution time:', totalTime, 'seconds')
        
        licence_Data = {'licence_plate':license_text}
        
        newData = {'vehicleData':licence_Data,
        'personData':personData,}
        #return {'licence_plate':license_text}       
        return json.dumps(newData , cls=NumpyEncoder)


obj = Inference() #class objet

@app.route('/insert', methods=['POST'])
def runMain():
    data = obj.main()
    return data


def transformImage(image):
    if str(type(image)) != "<class 'numpy.ndarray'>":
        try: # read image_url
            response = requests.get(image)
            img = Image.open(io.BytesIO(response.content))
        except: # read image_bytes
            img = Image.open(image)

        arr = np.uint8(img)

        image_shape = arr.shape
        if image_shape[2] != 3: # convering image to 3 channels for extracting embeddings
            arr = arr[:,:,:3]

        image_arr = cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)
        return image_arr
    
    return image


@app.route('/crowd', method=['POST'])
def crowd():
    try:
        image = request.files['image_path'] # image in bytes
    except:
        try:
            nparr = np.fromstring(request.data, np.uint8) # image in bytes from kafka
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        except:
            try:
                image = request.form['image_path'] # image_url
            except:
                logger.error("Error 400: Bad Input")
                return "Error 400: Bad Input", 400
    
    image = transformImage(image)
    

        
    crowd_count = obj.


if __name__ == '__main__': 
    pridict = Inference()
    weights, view_img, save_txt, imgsz, trace, device = pridict.parameters()
    # Initialize
    set_logging()
    device = select_device(device)
    half = device.type != 'cpu'  # half precision only supported on CUDA
    # Load model
    model = attempt_load(weights, map_location=device)  # load FP32 model
    stride = int(model.stride.max())  # model stride
    imgsz = check_img_size(imgsz, s=stride)  # check img_size
    if trace:
        model = TracedModel(model, device, imgsz)
    if half:
        model.half()  # to FP16
    #app.run(debug=True, host = '0.0.0.0', port=5000)
    app.run(debug=True)
