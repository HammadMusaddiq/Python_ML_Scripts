from ultralytics import YOLO

MODEL_PATH = "/mnt/sdc1/dl_work/rapidev_owlsense/models/yolov8/AIX/fixed-tars-classification-s-004/weights/best.pt"
model = YOLO(MODEL_PATH)
results = model.val()

# BEST ACCURACY: M - 88.7%
# BEST ACCURACY: N - 89.2%
# BEST ACCURACY: S - 87.2%