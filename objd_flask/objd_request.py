import requests
from detectron2.engine import DefaultPredictor
from detectron2.data import MetadataCatalog
from detectron2.config import get_cfg
from detectron2 import model_zoo
from detectron2.utils.visualizer import Visualizer
from skimage import io
import cv2
import matplotlib.pyplot as plt
import json
import os
from matplotlib import patches, text, patheffects

node_ip_objd = '192.168.18.24'
node_port_objd = '5002'

cfg = get_cfg()
model_file = "COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml"
cfg.merge_from_file(model_zoo.get_config_file(model_file))
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(model_file)
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.7
cfg.MODEL.DEVICE='cpu'
class_names = MetadataCatalog.get(cfg.DATASETS.TRAIN[0]).thing_classes
model = DefaultPredictor(cfg)

image_url = "http://192.168.18.33/osint_system/media_files/ess/st_fb_425/54377b03-4c61-481a-acb2-967dd58926ad.jpg"

response = requests.post(f"http://{node_ip_objd}:{node_port_objd}/", json={"imageUrl":image_url})
objd = response.json()["data"]
print(objd)
#print(type(objd))
objd_data = objd[0]

img = io.imread(image_url)
#img_cvt = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

# img_data = {"pred_boxes": [[3.2962e+02, 1.3569e+02, 3.8360e+02, 1.8008e+02], \
#         [1.7277e+02, 1.2007e+02, 2.6151e+02, 2.2755e+02], \
#         [3.0281e+02, 1.6476e+02, 3.1351e+02, 1.7393e+02], \
#         [4.0498e-01, 1.2827e+02, 5.6448e+01, 2.2276e+02], \
#         [3.8783e+02, 5.7938e+01, 3.9923e+02, 1.0046e+02], \
#         [1.1566e+02, 2.4811e+02, 2.1548e+02, 2.9309e+02], \
#         [3.7970e+02, 5.8208e+01, 3.8845e+02, 9.9713e+01], \
#         [3.4583e+02, 6.6553e+01, 3.5433e+02, 9.7481e+01], \
#         [4.0103e+02, 5.9063e+01, 4.1380e+02, 1.0101e+02], \
#         [3.7559e+02, 5.9213e+01, 3.8151e+02, 9.9661e+01], \
#         [3.5882e+02, 5.9792e+01, 3.6531e+02, 9.8114e+01], \
#         [3.3293e+02, 5.2902e+01, 4.5288e+02, 1.0331e+02], \
#         [3.6418e+02, 6.0367e+01, 3.6999e+02, 9.8836e+01], \
#         [3.6954e+02, 5.9640e+01, 3.7550e+02, 9.9363e+01], \
#         [3.8319e+02, 1.6636e+02, 4.2506e+02, 1.8432e+02], \
#         [4.1203e+02, 5.9557e+01, 4.2002e+02, 1.0123e+02], \
#         [3.5376e+02, 5.8761e+01, 3.6463e+02, 9.8161e+01]], 
#         'scores': [0.9933, 0.9882, 0.9794, 0.9231, 0.9047, 0.8534, 0.8440, 0.8035, 0.7291, 0.6549, 0.6519, 0.6392, 0.5959, 0.5581, \
#         0.5570, 0.5075, 0.5070], \
#         'pred_classes': [63, 56, 64, 58, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73, 73]}

# img_data2 = {'pred_boxes' : [[192.4766, 223.4982, 376.9117, 391.8551]],\
#                 'scores' : ['0.9933'],\
#                 'pred_classes': ['0']}

v = Visualizer(img[:, :, ::-1], MetadataCatalog.get(cfg.DATASETS.TRAIN[0]), scale=1.2)

#prediction_output = model(img_cvt)

# need to convert str list to int list for boxes

objd_data_predicted_axis = []
for axis in objd_data['predicted_axis']:
    objd_data_predicted_axis.append([float(val) for val in axis])

#print(objd_data_predicted_axis)


for _box,_score,_class in zip(objd_data_predicted_axis,objd_data['probability_score'],objd_data['object_classified']):
    v.draw_box(_box)
    v.draw_text("{}({}%)".format(str(_class),str(_score)),(_box[:2]))
v = v.get_output()
# print("DREW BOX")
img =  v.get_image()[:, :, ::-1]

plt.figure(figsize=(15,7.5))
plt.imshow(img)
plt.show(block=False)
input('press <ENTER> to continue')