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
import time

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

    
    def getCropImages(self, data,frame):
        cropImages = []
        for key, value in data.items():
            if key == "bbox":
                for box in value:
                    X = int(box[0]) #x
                    Y = int(box[1]) #y
                    W = int(box[2]) #w 
                    H = int(box[3]) #h
                    #rec = frame.copy()
                    #rec = cv2.rectangle(rec, (X, Y), (W, H), (255,0,0), 4)
                    crop = frame.copy()
                    cropped_image = crop[Y:H, X:W]
                    # cv2.imshow('Croped', cropped_image)
                    # cv2.imshow('Frame', rec)
                    # cv2.waitKey(0)
                    # cv2.destroyAllWindows()
                    cropImages.append(cropped_image)
        return cropImages        

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
        arr = np.uint8(img)
        image_shape = arr.shape
        x, y, _ = arr.shape

        arr = cv2.resize(arr, (640, 640), interpolation=cv2.INTER_AREA)
        if len(image_shape)<3:
            img = self.convert_2d_to_3d(img)
            arr = np.uint8(img)
            image_shape = arr.shape

        # if image_shape[2] != 3: # convering image to 3 channels for extracting embeddings
        #     arr = arr[:,:,:3]
        return arr

    
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
   
    def main(self):
        
        try:
            #pdb.set_trace()
            image = request.files['image_path']
            #print("Image Path recived",image)
            frame = self.transform(image)
        except:
            nparr = np.fromstring(request.data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR) 
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

        con1 = []
        bbox1 = []
        label1 = []
        if len(predictions) > 0:
            for each1 in predictions:
                lab = labels[int(each1[5])]
                if lab == 'car' or lab == 'truck' or lab == 'bus' or lab == 'motorbike':
                    if ((each1[4])*100) > 88:          #confidence
                        con1.append(float(each1[4])*100)
                        bbox1.append(each1[:4].cpu().detach().numpy())
                        label1.append(labels[int(each1[5])])
        else:
            logger.info("No vehicle is found!")
        data1 = {'confidence':con1,
                'bbox':bbox1,
                'label':label1}

        # time taken in retrieving car objects


        #getting crop image of car
        croppedImages = self.getCropImages(data1, frame)

        # get the end time yolo
        yet = time.time()
        # get the execution time of yolo
        yelapsed_time = yet - yst
        print('----------------------------------- Execution time of YOLO7 to extract all vechicle objects:', yelapsed_time, 'seconds')


        # get the start time ANPR
        nst = time.time()
        license_text = []
        for _, crop_image in enumerate(croppedImages):
            ##number plate detection
            licence_plate= self.getNumDetModel().plate_detection(crop_image)
            if(len(licence_plate)):
                license_text.append(licence_plate)
        
        # # get the end time ANPR
        net = time.time()
        # # get the execution time of ANPR
        nelapsed_time = net - nst
        print('----------------------------------- Execution time of OCR process:', nelapsed_time, 'seconds')
        totalTime = nelapsed_time + yelapsed_time
        print('----------------------------------- Total Execution time:', totalTime, 'seconds')

        return {'licence_plate':license_text}       
        #return json.dumps(data, cls=NumpyEncoder)



@app.route('/insert', methods=['POST'])
def runMain():
    obj = Inference() #class objet
    data = obj.main()
    return data


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
