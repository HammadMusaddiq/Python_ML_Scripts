import cv2
import math
import numpy as np
from PIL import Image

read_video = cv2.VideoCapture("video-clip3.mp4")

frameRate = 0.1 #it will capture image in each 1 second (10 images per second)- 10 FPS
sec = 0.0
count = 0
img_array = []
img_rgb = []

img_size = None

while read_video.isOpened():
    sec = round(sec, 2)
    read_video.set(cv2.CAP_PROP_POS_MSEC,sec*1000) 
    ret, frame = read_video.read()
    # if frame is read correctly ret is True
    
    if not ret:
        break

    count = count + 1
    
    #print(frame)
    decimal_part, number_part  = math.modf(sec)
    image_name = 'IMG'+str(int(number_part))+'Frame'+str(count)
    #print(image_name)
    
    sec = sec + frameRate
    
    cvt_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    image = Image.fromarray(np.uint8(cvt_frame)).convert('RGB')

    #image_link = ftp_connection(image_name, image)

    img_array.append(frame)
    img_rgb.append(image)

    height, width, layers = frame.shape

    img_size = (width,height)

    if count == 10: # 10 Frames for image name
        count = 0

    if cv2.waitKey(1) == ord('q'):
        break
        
    #read_video.release()
    #cv2.destroyAllWindows()

print(img_size)

video_fps = 10

# MP4V, mp4v, DIVX, XVID
out = cv2.VideoWriter('Frames_To_Video.avi',cv2.VideoWriter_fourcc(*'XVID'), video_fps, img_size)

for i in range(len(img_array)):
    out.write(img_array[i])
out.release()