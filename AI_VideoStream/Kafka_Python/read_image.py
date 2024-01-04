from asyncore import read
import base64
import cv2
import numpy as np
from PIL import Image
import io
import pickle


f = open("data.txt").read()

print(type(f))


import pdb; pdb.set_trace()
imdata = base64.b64decode(f)
im = pickle.loads(imdata)

image = Image.fromarray(im[...,::-1])

# img_buffer = str.encode(f)
# print(type(img_buffer))

# # imdata = base64.b64decode(img_buffer)
# # print(type(imdata))

# nparr = np.fromstring(img_buffer, np.uint8)
# img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR) # cv2.IMREAD_COLOR in OpenCV 3.1

# # i = cv2.imdecode(np.fromstring(imdata, dtype=np.uint8), cv2.IMREAD_COLOR)
# # print(i.shape)

# # read bytes with PIL
# # img = Image.open(io.BytesIO(imdata))
# # arr = np.uint8(img)
# # print(arr.shape)

import pdb; pdb.set_trace()
print("yes")