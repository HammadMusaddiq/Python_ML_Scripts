import cv2

# camera_user='admin'
# camera_pass='Admin12345'
# camera_ip='192.168.23.199'
# # live = 'rtsp://admin:Admin12345@192.168.23.199'
# live_feed = "rtsp://"+camera_user+":"+camera_pass+"@"+camera_ip+""

# cap = cv2.VideoCapture(live_feed, cv2.CAP_FFMPEG)

# #cap = cv2.VideoCapture()

# #cap.open(camera_port)

# while cap.isOpened():
#  # Capture frame-by-frame
#     ret, frame = cap.read()
# #     print(frame)

# # Our operations on the frame come here
# #     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

# # Display the resulting frame
#     cv2.imshow('frame',frame)

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # When everything done, release the capture
# cap.release()
# cv2.destroyAllWindows()


import subprocess
import threading
from multiprocessing import Process, Array
from frs_stream import FRS_Stream
import numpy as np
from PIL import Image
import datetime
import queue

from threading import Thread
from queue import Queue


lst = [1,2,3,4,5]


image_path = "/home/hammad/Downloads/1660651574685133.jpg",\
            "/home/hammad/Downloads/1660652654430102.jpg",\
            "/home/hammad/Downloads/1660652767599841.jpg",\
            "/home/hammad/Downloads/1660652848668055.jpg",\
            "/home/hammad/Downloads/1660727610685316.jpg",\
            "/home/hammad/Downloads/new1.jpg"


frs_model = FRS_Stream()


img_array = []


img = cv2.imread("/home/hammad/Downloads/new1.jpg")
img_array.append(img)


# a_set = set()
# for i in img:
#     a_set.update(set(i))



def plotAnnotation(bbox, image_array):    
    annotated_image = None
    label = "Unknown"
    for box in bbox:
        annotated_image = cv2.rectangle(image_array, (box[0], box[1]), (box[2]+box[0], box[3]+box[1]), (255,0,0), 3)
        labelled_image = cv2.putText(annotated_image, label, (box[0], box[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,0,0), 2)
    return labelled_image



def frs_fun(frame):
    print(frame.shape)

    face_prediction = frs_model.predict(frame)
    box = face_prediction['box']
    frame1 = plotAnnotation(box,frame)
    # frame_queue.put(frame1)

    cv2.imshow("im", frame1)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # queue.put(frame1)
    # return frame1


# def init(shared_arr_):
#     global shared_arr
#     shared_arr = shared_arr_ # must be inherited, not passed as an argument


# def tonumpyarray(mp_arr):
#     return np.frombuffer(mp_arr.get_obj())

# def f(i):
#     """synchronized."""
#     with shared_arr.get_lock(): # synchronize access
#         g(i)

# def g(i):
#     """no synchronization."""
#     arr = tonumpyarray(shared_arr)
#     arr[i] = -1 * arr[i]



# frame_queue = Queue()
# import pdb; pdb.set_trace()
# p1 = Process(target=frs_fun, args=(img, frame_queue))
# p1.start()
# p1.join()

p1 = Process(target=frs_fun, args=(img,))
p1.start()
p1.join()

# processes = dict()
# for img in img_array:
    
#     # import pdb; pdb.set_trace()
#     start = datetime.datetime.now()
#     # t1 = threading.Thread(target=frs_fun, args=(img,))
#     # processes[img] = multiprocessing.Process(target=frs_fun, args=(img, ))

#     # queue = multiprocessing.Queue()
#     # img1 = frs_fun(img)
#     # cv2.imshow("im", img1)
#     # cv2.waitKey(0)
#     # cv2.destroyAllWindows()

#     # arr = Array('d', img)
#     # processes[img] = Process(target=frs_fun, args=(arr,))

#     import ctypes

#     N = 10
#     shared_arr = Array(ctypes.c_double, N)
#     arr = tonumpyarray(shared_arr)

#     # shared_arr = multiprocessing.Array(ctypes.c_double, img)
#     # arr = tonumpyarray(shared_arr)
#     # N = 10

#     # with closing(multiprocessing.Pool(initializer=init, initargs=(shared_arr,))) as p:
#     #     # many processes access the same slice
#     #     stop_f = N // 10
#     #     p.map_async(f, [slice(stop_f)]*img)

#     #     # many processes access different slices of the same array
#     #     # assert img % 2 # odd
#     #     step = N // 10
#     #     p.map_async(g, [slice(i, i + step) for i in range(stop_f, N, step)])
#     # p.join()
#     # assert np.allclose(((-1)**M)*tonumpyarray(shared_arr), arr_orig)



#     processes[img] = Process(target=frs_fun, args=(arr,))
#     processes[img].start()
#     processes[img].join()

#     end = datetime.datetime.now()
#     print(end-start)





# processes = dict()
# for i in lst :
#     processes[i] = multiprocessing.Process(target=print_square, args=(i, ))
#     processes[i].start()
#     # processes[i].join()
#     print(processes[i].pid)
