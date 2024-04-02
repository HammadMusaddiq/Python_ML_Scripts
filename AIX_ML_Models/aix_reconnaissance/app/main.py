from fastapi import FastAPI, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import utils as api_utils
import constants
import uvicorn
from datetime import datetime
import time
from collections import defaultdict

reconnaissance_model, reconnaissance_labels = api_utils.get_model(
    constants.TRAINED_MODEL_PATH,
    constants.TRAINED_MODEL_LABELS_PATH,
    constants.CONFIDENCE_THRESHOLD,
)

kafka_producer = api_utils.KafkaHandler(kafka_ip="10.100.160.100:9092")

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def index():
    return {"message": "API is working..."}


@app.post("/test_pic")
async def test_pic(
    img: UploadFile = None,
):
    if img:
        img = await img.read()
        img = cv2.imdecode(np.frombuffer(img, np.uint8), -1)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        cv2.imwrite("test.png", img)
        return {"message": "Image saved"}
    else:
        return {"message": "Please provide an image"}


def process_img(img):
    start_time = time.time()
    preds = api_utils.get_detections(
        img,
        reconnaissance_model,
    )
    # file_name = f'res__{datetime.now().strftime("%d_%m_%Y__%H_%M_%S")}'
    # preds.export_visuals(
        # export_dir="/resources/test_res/",
        # file_name=file_name,
        # text_size=0.1,
        # rect_th=1,
    # )
    response = api_utils.decode_results(
        results=preds,
        start_time=start_time,
    )
    object_count = defaultdict(int)
    for obj in response:
        object_count[obj["class"]] += 1

    data_dict = {
        "detections": response,
        "label": reconnaissance_labels,
        "object_count": object_count,
    }
    kafka_producer.send_data("reconnaissance_preds", data_dict)
    

@app.post("/get_predictions")
async def get_predictions(
    background_tasks: BackgroundTasks,
    img_url: str = None,
    img: UploadFile = None,
):
    if img_url:
        if "://" in img_url:
            img = api_utils.get_image_from_url(img_url)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    elif img:
        img = await img.read()
        img = cv2.imdecode(np.frombuffer(img, np.uint8), -1)
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)

    else:
        return {"message": "Please provide an image"}

    background_tasks.add_task(process_img, img)

    return {
        "message": "start processing"
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8091)
