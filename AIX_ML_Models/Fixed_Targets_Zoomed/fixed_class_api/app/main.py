from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from enum import Enum
import cv2
import numpy as np
import utils as api_utils
import constants
import uvicorn


# zoomed_model = api_utils.get_model(constants.WEIGHTS_PATH_ZOOMED)
satellite_model = api_utils.get_model(constants.WEIGHTS_PATH_SATELLITE)

class ModelType(str, Enum):
    # zoomed = "zoomed"
    satellite = "satellite"

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


@app.post("/get_predictions")
async def get_predictions(
    # model_type: ModelType,
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
        print(img.shape)

    else:
        return {"message": "Please provide an image"}


    # if model_type == "zoomed":
    #     model = zoomed_model
    # if model_type == "satellite":
    #     model = satellite_model
    # else:
    #     return {"message": "Please provide a valid model type"}
    model = satellite_model

    # cv2.imwrite("test.png", img)
    results = model(img)

    response = api_utils.decode_results(
        # classes=model.names,
        classes = {0: 'Urban_Area', 1: 'Coastal'},
        preds=results,
    )

    return response


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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8089)
