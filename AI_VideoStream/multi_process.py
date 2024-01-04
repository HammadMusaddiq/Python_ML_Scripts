# import the necessary packages
import multiprocessing as mp
from multiprocessing import Pool, cpu_count, Process, Lock

import os
from tkinter import image_names
import cv2

from frs_stream import FRS_Stream





def rgbFun(img):
    image = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    return image


def read_image_numpy(image_array):
    pid = os.getpid()
    print("process id: " + str(pid))

    # acquire the lock (for handling one process at a time) if not then OS schedule process
    # lock.acquire() 

    image_shape = image_array.shape
    print(image_shape)

    image_rgb = rgbFun(image_array)
    print(image_rgb.shape)

    face_prediction = frs_model.predict(image_array)
    box = face_prediction['box']
    print(box)
    
    # release the lock
    # lock.release()


# determine the number of concurrent processes to launch when, CPU Cores
# distributing the load across the system, then create the list of process IDs
# procs = cpu_count()
# procIDs = list(range(0, procs))
# print(procIDs)


if __name__ == "__main__":

    # frs = FRS_Stream()

    # img = cv2.imread("/home/hammad/Downloads/new1.jpg")

    # output = frs.predict(img)
    # print(output)



    frs_model = FRS_Stream()

    image_path = "/home/hammad/Downloads/new1.jpg"

    lock = Lock()
    img = cv2.imread(image_path)

    pool = Pool(processes=1)
    pool.map(read_image_numpy,img)
    pool.close()
    pool.join()

    # read_image_numpy(img,lock)

    # processes = [Process(target=read_image_numpy, args=((os.path.join(path,filename)) , lock,)) for filename in files if filename != "Results"]
    # p = Process(target=read_image_numpy, args=(img,lock, ))
    # # print(processes)
    # p.start()1
    # p.join()
    
    # start the processes
    # for process in processes:
    #     process.start()
        

    # # wait for completion
    # for process in processes:
    #     process.join()
    #     print("join ",process.pid)

    # for file_name in files:
    #     if file_name != "Results":
    #         img_path = os.path.join(path,file_name)

            

    #         # print(file_name)
    #         # proc1 = Process(target=read_image_numpy, args=(img_path,))
    #         # proc2 = Process(target=read_image_numpy, args=(img_path,))
    #         # proc1.start()
    #         # print("processes :",os.getpid())
    #         # proc2.start()
    #         # print("processes :",os.getpid())




        #     img123o = read_image_numpy(img_path)
        #     shapeX, shapeY, _ = img123o.shape
        #     if shapeX > 900 and shapeY > 900:
        #         img12 = cv2.resize(img123o, (900, 900))
        #     else:
        #         img12 = img123o.copy()
        #     # function parameters that can be changed
        #     # function parameters for MTCNN are (mtcnnDetectFace,mtcnnDetectScore)
        # obj, score, name, bbox = detectface(mtcnnDetectFace, mtcnnDetectScore, img12)
        #     # j is for no crop image and bbox on the orignal image
        #         # If other than 1, than you will get the crop image of face
        #     j = 1
        # saveFig(obj, score, name, bbox, img12, j)
        #     # function parameters for RetinaFace are (retinaDetectFace,retinaDetectScore)
        # obj, score, name, bbox = detectface(retinaDetectFace, retinaDetectScore, img12)
        # saveFig(obj, score, name, bbox, img12, j)

        #     # proc1.join()
        #     # proc2.join()





# face verification
# verification = DeepFace.verify(img1_path = "/home/haseeb-javaid/Downloads/Pics/1.jpg", img2_path = "/home/haseeb-javaid/Downloads/Pics/2.jpg", enforce_detection = True)

# print(verification)

# analysis = DeepFace.analyze(img_path = "/home/haseeb-javaid/Downloads/1.jpg", actions = ["age", "gender", "emotion", "race"])
# print(analysis)


# face recognition
# recognition = DeepFace.find(img_path = "img.jpg", db_path = "C:/facial_db", detector_backend = detectors[0])
# frame = cv2.imread('/home/haseeb-javaid/Downloads/sport.png')

# RetinaNet = DeepFace.detectFace('/home/haseeb-javaid/Downloads/sport.png', detector_backend = detectors[4])
# mtcnn = DeepFace.detectFace("/home/haseeb-javaid/Downloads/sport.png", detector_backend = detectors[2])

# #dlib = DeepFace.detectFace("/home/haseeb-javaid/Downloads/1.jpg", detector_backend = detectors[3])
# ssd = DeepFace.detectFace("/home/haseeb-javaid/Downloads/sport.png", detector_backend = detectors[1])
# opencv = DeepFace.detectFace("/home/haseeb-javaid/Downloads/sport.png", detector_backend = detectors[0])
# scale = 224
# imS = cv2.resize(frame, (scale, scale))

# while True:
#     cv2.imshow('Orignal Image',imS)
#     cv2.imshow('RetinaNet Face Detection',RetinaNet)
#     cv2.imshow('mtcnn Face Detection',mtcnn)

#     #cv2.imshow('dlib Face Detection',dlib)
#     cv2.imshow('ssd Face Detection',ssd)
#     cv2.imshow('opencv Face Detection',opencv)
#     if cv2.waitKey(20) & 0xFF == 27:
#         break
# cv2.destroyAllWindows()