import pandas as pd 
import os 
import glob, tqdm
from sklearn.model_selection import train_test_split
import numpy as np
import shutil

images_path = []
for img_path in glob.glob("/home/hammad/Downloads/Python Files/yolo_train/Data/train/images/*"):
    images_path.append(img_path)

print(len(images_path))
# print(images_path[:5])


def split_img_label(data_train, data_test, data_val):

    pw_directory = "Data/Splitted_Data/"
    split_folders = ['train', 'val', 'test']
    data_folders = ['images', 'labels']

    img_directory = "Data/train/images/"
    label_directory = "Data/train/labels/"

    if not os.path.exists(pw_directory):
        os.mkdir(pw_directory)

    for m_folder in split_folders:
        if not os.path.exists(pw_directory + m_folder):
            os.mkdir(pw_directory + m_folder)
        for d_folder in data_folders:
            if not os.path.exists(pw_directory + m_folder + "/" + d_folder):    
                os.mkdir(pw_directory + m_folder + "/" + d_folder)

  
    # # Train folder
    for data in data_train:
        data_path = data.rsplit('.',1)[0]
        shutil.copy2(img_directory + data, pw_directory + "train/" + "images/")
        shutil.copy2(label_directory + data_path +".txt" , pw_directory + "train/" + "labels/")

    # # Val folder
    for data in data_val:
        data_path = data.rsplit('.',1)[0]
        shutil.copy2(img_directory + data, pw_directory + "val/" + "images/")
        shutil.copy2(label_directory + data_path +".txt" , pw_directory + "val/" + "labels/")

    # # Test folder
    for data in data_test:
        data_path = data.rsplit('.',1)[0]
        shutil.copy2(img_directory + data, pw_directory + "test/" + "images/")
        shutil.copy2(label_directory + data_path +".txt" , pw_directory + "test/" + "labels/")
   


list_img=[img for img in os.listdir("/home/hammad/Downloads/Python Files/yolo_train/Data/train/images/")]
list_txt=[img for img in os.listdir("/home/hammad/Downloads/Python Files/yolo_train/Data/train/labels/")]

# Train, Val, Test Split (60*20*20)
X_train, X_test, y_train, y_test = train_test_split(list_img, list_txt, test_size=0.2, random_state=1)
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.25, random_state=1) # 0.25 x 0.8 = 0.2

# Function split 
print(len(X_train),len(y_train))
print(len(X_val),len(y_val))
print(len(X_test),len(y_test))

split_img_label(X_train, X_val, X_test)
print("Completed................")
