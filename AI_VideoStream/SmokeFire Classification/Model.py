import cv2
import os
import sys
import math
import numpy as np
import tflearn
from tflearn.layers.core import *
from tflearn.layers.conv import *
from tflearn.layers.normalization import *
from tflearn.layers.estimator import regression
from PIL import Image
import os

#os.environ['CUDA_VISIBLE_DEVICES'] = '0'



imgsz=(224, 224)  # inference size (height, width)
classes=['Clear', 'Fire/Smoke']
# load model


rows = 224
cols = 224


def construct_firenet (x,y, training=False):

        # Build network as per architecture in [Dunnings/Breckon, 2018]

        network = tflearn.input_data(shape=[None, y, x, 3], dtype=tf.float32)

        network = conv_2d(network, 64, 5, strides=4, activation='relu')

        network = max_pool_2d(network, 3, strides=2)
        network = local_response_normalization(network)

        network = conv_2d(network, 128, 4, activation='relu')

        network = max_pool_2d(network, 3, strides=2)
        network = local_response_normalization(network)

        network = conv_2d(network, 256, 1, activation='relu')

        network = max_pool_2d(network, 3, strides=2)
        network = local_response_normalization(network)

        network = fully_connected(network, 4096, activation='tanh')
        # if(training):
        #     network = dropout(network, 0.5)

        network = fully_connected(network, 4096, activation='tanh')
        # if(training):
        #     network = dropout(network, 0.5)

        network = fully_connected(network, 2, activation='softmax')

        # if training then add training hyperparameters

        # if(training):
        #     network = regression(network, optimizer='momentum',
        #                         loss='categorical_crossentropy',
        #                         learning_rate=0.001)

        # constuct final model

        model = tflearn.DNN(network, checkpoint_path='firenet',
                            max_checkpoints=1, tensorboard_verbose=2)

        return model


class Model:
    model =''

    def __init__(self, 
    imgsz=(224,224)
    ):
        self.model = construct_firenet (224, 224, training=False)
        self.model.load(os.path.join("firenet"),weights_only=True)


    def convert_2d_to_3d(self, image):
        image.save('current.png')
        img = cv2.imread('current.png')
        os.remove('current.png')
        return img

    def transform(self, image_bytes):
        img = Image.open(image_bytes)
        arr = np.uint8(img)
        image_shape = arr.shape
        if len(image_shape)<3:
            img = self.convert_2d_to_3d(img)
            arr = np.uint8(img)
            image_shape = arr.shape
        return arr

    def predict(self, test):

        resized_frame = cv2.resize(test, imgsz, cv2.INTER_AREA)

        test = np.expand_dims(resized_frame, 0)
        predicted1 = self.model.predict(test)
        print(predicted1)
        print(predicted1[0].argmax())
        if round(predicted1[0][0]) == 1:
            pred = 1
        else:
            pred = 0
        

        return pred

        




   
