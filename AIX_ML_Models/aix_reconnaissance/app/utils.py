import numpy as np
import constants, requests, io
from PIL import Image

from sahi import AutoDetectionModel
from sahi.predict import get_sliced_prediction
import time

# CHECK these functions to load larger tiffs
# from sahi.utils.cv import read_image, read_image_as_pil, read_large_image
# loaded_image = read_image(constants.TEST_IMAGE_PATH)

from kafka import KafkaProducer
from json import dumps

class KafkaHandler:

    def __init__(self, kafka_ip=""):
        self.producer = KafkaProducer(bootstrap_servers=[kafka_ip], 
                                    value_serializer=lambda x: dumps(x).encode('utf-8'))

    def send_data(self, topic="sample", data={}):
        self.producer.send(topic, value=data)


def get_model(weights_path: str, labels_path:str, confidence_threshold: float):
    # load model
    model = AutoDetectionModel.from_pretrained(
        model_type="yolov5",
        model_path=weights_path,
        confidence_threshold=confidence_threshold,
        device="cuda:0",  # "cpu" or "cuda:0"
    )
    
    labels = []
    with open(labels_path, "r") as label_file:
        labels = label_file.readline().split(";")

    return model, labels


def get_image_from_url(img_url: str):
    response = requests.get(img_url)
    img = Image.open(io.BytesIO(response.content))
    return np.uint8(img)

def get_detections(image, model):
    results = get_sliced_prediction(
        image,
        model,
        slice_height=constants.SLICE_HEIGHT,
        slice_width=constants.SLICE_WIDTH,
        overlap_height_ratio=constants.OVERLAP_HEIGHT_RATIO,
        overlap_width_ratio=constants.OVERLAP_WIDTH_RATIO,
    )
    return results

def decode_results(results, start_time):
    infer_time = time.time() - start_time
    return [
        {
            "class": obj.category.name,
            "confidence": obj.score.value,
            "bbox": [float(n) for n in obj.bbox.to_xywh()],
            "inference_time": infer_time,
        }
        for obj in results.object_prediction_list
    ]
