import requests
from PIL import Image
import io
import numpy as np
from ultralytics import YOLO


def get_model(weights_path: str):

    # load model
    model = YOLO(weights_path)
    # perform a warmup inference
    model(np.random.rand(1024, 1024, 3).astype(np.uint8))

    return model


def get_image_from_url(img_url: str):
    response = requests.get(img_url)
    img = Image.open(io.BytesIO(response.content))
    return np.uint8(img)


def decode_results(classes, preds):
    probs_cpu = preds[0].probs.cpu().numpy()
    predicted_class = classes[np.argmax(probs_cpu)]

    probs_dict = {}
    for i in range(len(classes)):
        if "bigcities" in str(classes[i]).lower():
            probs_dict["Urban Area"] = float(probs_cpu[i])
        else:
            probs_dict[classes[i]] = float(probs_cpu[i])

    predicted_class = (
        "Urban Area" if "bigcities" in str(predicted_class).lower() else predicted_class
    )

    response = {
        "class": predicted_class,
        "predictions": probs_dict,
    }
    return response
