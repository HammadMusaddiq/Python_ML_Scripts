import json, numpy as np, cv2, io, requests, logging
from PIL import Image
from flask import Flask, request
from MODEL import Model


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

logger.info("Application Started")



non_sattelite_model = Model()

app = Flask(__name__)

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

video = False #flag to check if it is a video or an image


@app.route('/insert', methods=['POST'])
def main():
    logger.info("Starting Image Inference")
    video = False
    try:
        try:
            image = request.files['image_path']        
            frame = non_sattelite_model.transform(image)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except:
            try:
                nparr = np.fromstring(request.data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            except:
                link =request.form['image_path']
                response = requests.get(link)
                img = Image.open(io.BytesIO(response.content))
                arr = np.uint8(img)
                frame = arr
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


        img0 = frame  # BGR
        
        # Padded resize
        img = non_sattelite_model.letterbox(img0, non_sattelite_model.img_size, stride=non_sattelite_model.stride)[0]
        
        # Convert
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        img = np.ascontiguousarray(img)

        source = img #np.expand_dims(frame, 0)
        
        pred, ploted_image_link = non_sattelite_model.detect(source, img0, video)

        labels = ['Civilian_Vehicle', 'Gun', 'Military_Tank', 'Military_Vehicle', 'Person', 'Pistol', 'Soldier']
        predictions = pred[0]
        con = []
        bbox = []
        label = []
        target = "No Target Found"
        if len(predictions) > 0:
            for each in predictions:
                con.append(float(each[4])*100)
                bbox.append(each[:4].cpu().detach().numpy())
                label.append(labels[int(each[5])])

        for i in label:
            if i in ['Military_Mank', 'Military_Vehicle', 'Soldier']:
                target = "Land Target"
        
        object_count = {}
        for L in labels:
            object_count[L] = label.count(L)

        data = {'processed_url':ploted_image_link,
                'confidence':con,
                'bbox':bbox,
                'label':label,
                'object_count': object_count,
                'target':target}

        print(data)

        return json.dumps(data, cls=NumpyEncoder)
    except Exception as E:
        print(E)
        return {}

@app.route('/video', methods=['POST'])
def video():
    logger.info("Starting Video Inference")
    video = True
    try:
        try:
            image = request.files['image_path']        
            frame = non_sattelite_model.transform(image)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except:
            try:
                nparr = np.fromstring(request.data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            except:
                link =request.form['image_path']
                response = requests.get(link)
                img = Image.open(io.BytesIO(response.content))
                arr = np.uint8(img)
                frame = arr
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


        img0 = frame  # BGR
        
        # Padded resize
        img = non_sattelite_model.letterbox(img0, non_sattelite_model.img_size, stride=non_sattelite_model.stride)[0]
        
        # Convert
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        img = np.ascontiguousarray(img)

        source = img #np.expand_dims(frame, 0)
        
        pred, ploted_image_link = non_sattelite_model.detect(source, img0, video)


        labels = ['Civilian_Vehicle', 'Gun', 'Military_Tank', 'Military_Vehicle', 'Person', 'Pistol', 'Soldier']

        predictions = pred[0]
        con = []
        bbox = []
        label = []
        target = "No Target Found"
        if len(predictions) > 0:
            for each in predictions:
                con.append(float(each[4])*100)
                bbox.append(each[:4].cpu().detach().numpy())
                label.append(labels[int(each[5])])
        
        for i in label:
            if i in ['military_tank', 'military_vehicle', 'soldier']:
                target = "Land Target"

        object_count = {}
        for L in labels:
            object_count[L] = label.count(L)

        data = {'processed_url':ploted_image_link.decode('utf-8'),
                'confidence':con,
                'bbox':bbox,
                'label':label,
                'object_count': object_count,
                'target':target}

        print(data.keys())

        return json.dumps(data, cls=NumpyEncoder)
    except Exception as E:
        print(E)
        return {}

if __name__ == '__main__':

    app.run(debug=True)

