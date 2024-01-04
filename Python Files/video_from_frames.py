
import cv2
import numpy as np
import glob

# vidcap = cv2.VideoCapture('/home/hammad/Downloads/Videos/1664965651288388.avi')
vidcap = cv2.VideoCapture("http://10.100.160.105/AIX/Videos/167567637247364/German%20soldier%20throws%20grenade_1%20(2)%20(1).mov",  cv2.CAP_FFMPEG)

fps = vidcap.get(cv2.CAP_PROP_FPS)
frames = list()

for i in range(100):
    success, image = vidcap.read()
    frames.append(image)

# MP4V , mp4v -> (mp4)
# DIVX , XVID -> (avi)
height, width, layers = image.shape
size = (width,height)

v_complete_path = ("video_from_frames.mp4")

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
# fourcc = -1

out = cv2.VideoWriter(v_complete_path, fourcc, int(fps), size)
 
for i in range(len(frames)):
    out.write(frames[i])
out.release()


import subprocess
# subprocess.run(["ffmpeg","-i","video_from_frames.avi","-c:v","copy","-c:a","copy","-y","output.mp4"])
subprocess.run(["ffmpeg","-i","video_from_frames.mp4","-y","output.mp4"])


