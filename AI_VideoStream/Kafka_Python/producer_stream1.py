from datetime import datetime
import time
import json
from kafka import KafkaProducer
import cv2
from datetime import datetime
import random
import uuid
import base64
import pickle

def json_serializer(data):
    return json.dumps(data).encode("utf-8")


def send_data(data):
    
    producer = KafkaProducer(bootstrap_servers=['10.100.103.125:9092'], value_serializer=json_serializer)
    producer.send("ai-live-feed", data)

# path = "/home/hammad/Downloads/imran3.jpeg"
path = "/home/hammad/Downloads/Face Recognition (Pictures)/Owlsense/Ahmed Faraz/IMG_2016.jpg"

img = cv2.imread(path)
dim = (540, 480)

if img.shape[0] >= 1000 or img.shape[1] >= 1000:
    img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)


# cv2.imshow("img", img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# img1 = img.tobytes().decode("latin-1")
# im_b64 = base64.b64encode(img1).decode("utf8")

imdata = pickle.dumps(img)
img = base64.b64encode(imdata).decode('ascii')

# jstr = json.dumps({"image": base64.b64encode(imdata).decode('latin-1')})
# print(type(jstr))

# with open("data.txt", 'w', encoding='utf-8') as f:
#     f.write(img)
#     f.close()


test = {"image" : img}

for i in range(2):
    send_data(test)

# print(type(img1))
