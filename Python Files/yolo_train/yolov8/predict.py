from ultralytics import YOLO
import numpy as np

MODEL_PATH = "/mnt/sdc1/dl_work/rapidev_owlsense/models/yolov8/AIX/fixed-tars-classification/weights/best.pt"
IMG_SOURCE = "/mnt/sdc1/dl_work/rapidev_owlsense/datasets/classfication/to_train_splits/test/Watercraft/Watercraft175.jpeg"

model = YOLO(MODEL_PATH)
results = model(IMG_SOURCE)
print(f"Classes {model.names}")
print(f"Results: {results}")

predicted_class = model.names[np.argmax(results[0].probs.cpu().numpy())]
print(f"Predicted class: {predicted_class}")