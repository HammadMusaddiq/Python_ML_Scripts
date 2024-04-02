import tensorflow as tf
import cv2
import numpy as np
import os
import flask

custom = tf.keras.models.load_model('custom_model_smoke.hdf5')
# efficientnet = tf.keras.models.load_model('efficientnet_smoke.hdf5')
resnet = tf.keras.models.load_model('resnetlat.hdf5')
custom_1 = tf.keras.models.load_model('fire&smokecustom10.hdf5')
custom_2 = tf.keras.models.load_model('custom50.hdf5')
vgg16 = tf.keras.models.load_model('vgg16.hdf5')

classes=['NoFile', 'Fire/Smoke']

images = os.listdir('test_folder/')

# vid = cv2.VideoCapture()

# print(test_img.shape)

camera_user='admin'
camera_pass='Admin12345'
camera_ip='192.168.23.199'

# live = 'rtsp://admin:Admin12345@192.168.23.199'


live_feed = "rtsp://"+camera_user+":"+camera_pass+"@"+camera_ip+""

vid = cv2.VideoCapture(live_feed, cv2.CAP_FFMPEG)

while(vid.isOpened()):
    ret, frame = vid.read()

    resized_frame = cv2.resize(frame, (640,640), cv2.INTER_AREA)

    test = np.expand_dims(resized_frame, 0)

    predicted3 = custom.predict(test)[0]
    predicted2 = custom_2.predict(test)[0]
    # predicted1 = custom_1.predict(test)[0]
    predicted4 = resnet.predict(test)[0]
    predicted5 = vgg16.predict(test)[0]

    # print(predicted4,predicted2,predicted3, predicted5)


    pred = (predicted4.round()+predicted2.round()+predicted3.round()+predicted5.round())/4
    # pred = (predicted4.round()+predicted5.round())/2
    # pred = predicted5
    print(pred)
    if pred>0.70:
        pred=1
    else:
        pred=0

    if pred==1:
        final=cv2.putText(resized_frame, 'Fire/Smoke', (10,25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2, cv2.LINE_AA)
    else:
        final=cv2.putText(resized_frame, 'Normal', (10,25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2, cv2.LINE_AA)
    
    cv2.imshow('Image',final)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


# for test_img in images:
#     print(test_img)
#     test_img = cv2.imread('test_folder/'+str(test_img))

#     test_img = cv2.resize(test_img, (640,640), cv2.INTER_AREA)

#     test = np.expand_dims(test_img, 0)
#     predicted3 = custom.predict(test)[0]
#     predicted2 = custom_2.predict(test)[0]
#     predicted1 = custom_1.predict(test)[0]
#     predicted4 = resnet.predict(test)[0]
#     predicted5 = vgg16.predict(test)[0]
    
#     print('1:     '+str(predicted1)+'\n2:     '+str(predicted2)+'\n3:     '+str(predicted3)+'\n4:     '+str(predicted4)+'\n5:     '+str(predicted5))


vid.release()
# Destroy all the windows
cv2.destroyAllWindows()


