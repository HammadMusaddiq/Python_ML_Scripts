# from comet_ml import Experiment
# Experiment.log_metrics()
# Experiment.log_parameters()

from ultralytics import YOLO

import os

os.environ["COMET_API_KEY"] = "dNY2h49GzKmaSlrHTFhcs5LJl"


# MODEL_PATH = "/mnt/sdc1/dl_work/rapidev_owlsense/models/yolov8/AIX/fixed-tars-classification2/args.yaml"

MODEL_TYPE_CLASSIFICATION = {
    "m": {"weights": "yolov8m-cls.pt", "imgsz": 1024, "batch": 8},
    "n": {"weights": "yolov8n-cls.pt", "imgsz": 384, "batch": 16},
    "s": {"weights": "yolov8s-cls.pt", "imgsz": 608, "batch": 8},
}

MODEL_TYPE_DETECTION = {
    "m": {"weights": "yolov8m.pt", "imgsz": 1024, "batch": 8, "data": "yolov8m.yaml"},
    "n": {"weights": "yolov8n.pt", "imgsz": 384, "batch": 16, "data": "yolov8n.yaml"},
    "s": {"weights": "yolov8s.pt", "imgsz": 608, "batch": 8, "data": "yolov8s.yaml"},
}


def train_model(model_type):
    model = YOLO(MODEL_TYPE_DETECTION[model_type]["weights"])
    results = model.train(
        project="AIX",
        name="DETECTION",
        # data=MODEL_TYPE_DETECTION[model_type]['data'],
        data="/mnt/sdc1/dl_work/rapidev_owlsense/models/yolov8/cls_data.yaml",    
        imgsz=MODEL_TYPE_DETECTION[model_type]["imgsz"],
        epochs=20,
        batch=MODEL_TYPE_DETECTION[model_type]["batch"],
        cache="ram",
        # workers=1,
        # resume=MODEL_PATH,
    )
    return results

# Create an experiment with your api key
# experiment = Experiment(
#     api_key="dNY2h49GzKmaSlrHTFhcs5LJl",
#     project_name="general",
#     workspace="subtain-malik-theowlsense",
# )

def main():
    train_model("s")

if __name__ == "__main__":
    main()