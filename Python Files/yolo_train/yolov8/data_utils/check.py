from pathlib import Path
import cv2
from tqdm import tqdm

INPUT_DIR = "/media/subait-malik-ml/datasets/satellite/full-scale/zoomed_imagery_train/test"

for path in tqdm(Path(INPUT_DIR).rglob("*")):
    if path.is_file():
        img = cv2.imread(str(path))
        try:
            shape = img.shape
        except Exception as e:
            print(path)
            print(e)