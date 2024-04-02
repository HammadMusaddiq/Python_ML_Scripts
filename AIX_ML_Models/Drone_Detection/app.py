from fastapi import FastAPI, UploadFile
import cv2, numpy as np, logging, requests, io, json, uvicorn, base64
from Model import MODEL
from PIL import Image

#logging Initialization
logger = logging.getLogger(__name__)
if logger.hasHandlers():
    logger.handlers.clear()

formatter = logging.Formatter('%(asctime)s | %(name)s |  %(levelname)s | %(message)s') 
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('app.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

logger.info("Application Started")


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


app = FastAPI()

drone_detector = MODEL()


@app.get('/')
async def drone_app():
    return "API is Live"

@app.post("/insert")
async def get_prediction(
    image_url: str = None,
    image_path: UploadFile = None
):  
    logger.info("Image Inference Started")
    try:        #Get image from the Requests
        try:
            contents = await image_path.read()
            img = Image.open(io.BytesIO(contents))
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except:
            try:
                contents = await image_path.body()
                nparr = np.fromstring(contents, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            except:
                # link = await image_url.form()
                response = requests.get(image_url)
                img = Image.open(io.BytesIO(response.content))
                arr = np.uint8(img)
                frame = arr
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    except Exception as E:
        logger.error(f"An exception {E} has occured while taking the image from the request")
        
    
    ####-----------------------------Perform Inference--------------------------------####
    try:
        results = drone_detector.predict(frame)
        logger.info("Model Inference Successfull")
    except Exception as E:
        logger.error(f"An exception {E} has occured while performing predictions")
    
    
    ####-------------------------------Results Processing-------------------------------#####
    try:
        class_labels = ['Drone']
        for result in results:
            res = result.boxes
            bboxes = res.xyxy.numpy()
            confs = res.conf.numpy()
            labels = res.cls.numpy()
            con = []
            bbox = []
            lab = []
            for box, conf, label in zip(bboxes, confs, labels):
                bbox.append(np.asarray(box))
                con.append(int(conf*100))
                lab.append(class_labels[int(label)])
            #plot on image
            for b, c, l in zip(bbox, con, lab):
                single_label = f'{l} {c:.2f}'
                drone_detector.plot_one_box(b, frame, label=single_label)
    except Exception as E:
        logger.error(f"An exception {E} has occured while processing the predictions")
        
    #stor image on FTP
    try:
        image_link = drone_detector.store_image_on_ftp(frame)
        logger.info(f"Success: Image stored to FTP, Image Link:{image_link}")
    except Exception as e:
        logger.error(f"An exception {E} has occured while uploading Images on FTP")
        image_link=''

    object_count = {}
    for L in lab:
        object_count[L] = lab.count(L)

    data = {'object_count': object_count,
            'confidence':con,
            'bbox':bbox,
            'label':lab,
            'image_link':image_link}
    # return data
    try:
        return json.dumps(data, cls=NumpyEncoder)
    except Exception as E:
        logger.error(f"An exception {E} has occured while returning the data.")

@app.post("/video")
async def get_video(
    image_url: str = None,
    image_path: UploadFile = None
):  
    logger.info("Video Inference Strarted")
    ####-----------------------Getting Image from Request---------------------####
    try: 
        try:
            contents = await image_path.read()
            nparr = np.frombuffer(contents, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        except:
            # link = await image_url.form()
            response = requests.get(image_url)
            img = Image.open(io.BytesIO(response.content))
            arr = np.uint8(img)
            frame = arr
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    except Exception as E:
        logger.error(f"An exception {E} has occured while taking the image from the request")

    
    
    ####-------------------------Perform Inference---------------------####
    try:
        results = drone_detector.predict(frame)
        logger.info(f"Infernece Successful")
    except Exception as E:
        logger.error(f"An exception {E} has occured while performing predictions")
    
    
    ####--------------------------Results Processing---------------------####
    try:
        class_labels = ['Drone']
        for result in results:
            res = result.boxes
            bboxes = res.xyxy.numpy()
            confs = res.conf.numpy()
            labels = res.cls.numpy()
            con = []
            bbox = []
            lab = []
            for box, conf, label in zip(bboxes, confs, labels):
                bbox.append(np.asarray(box))
                con.append(int(conf*100))
                lab.append(class_labels[int(label)])
            #plot on image
            for b, c, l in zip(bbox, con, lab):
                single_label = f'{l} {c:.2f}'
                drone_detector.plot_one_box(b, frame, label=single_label)
    except Exception as E:
        logger.error(f"An exception {E} has occured while processing the predictions")
    
    try:
        im0 = drone_detector.create_request_args(frame)
        im0 = base64.b64encode(im0)
    except Exception as E:
        logger.error(f"An exception {E} has occured while converting image to base64(bytes)")



    object_count = {}
    for L in lab:
        object_count[L] = lab.count(L)

    data = {'object_count': object_count,
            'confidence':con,
            'bbox':bbox,
            'label':lab,
            'image_bytes':im0.decode('utf-8')}
    
    try:
        return json.dumps(data, cls=NumpyEncoder)
    except Exception as E:
        logger.error(f"An exception {E} has occured while returning the data.")

    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)