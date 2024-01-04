
from ftplib import FTP
import io
import json
from ftplib import FTP
import random
import datetime
import requests
from PIL import Image
import numpy as np
import cv2

node_ip_ftp = "10.100.103.114"
node_port_ftp = 21
auth_user_ftp = 'microcrawler'
auth_pass_ftp = 'rapidev'

node_ip_wod = "10.100.103.200"
node_port_wod = 5017

weapon_post_url = "http://" + str(node_ip_wod) + ":" + str(node_port_wod) + "/insert"
BASE_URL = "http://" + node_ip_ftp + "/osint_system/media_files/Weapon_Detection/"

# FTP Server Connection
ftp = None


def connect():
    global ftp
    ftp = FTP()
    try:
        ftp.connect(node_ip_ftp, int(node_port_ftp))
        return True
    except Exception as e:
        print(e)
        return False


def login():
    global ftp
    try:
        ftp.login(auth_user_ftp, auth_pass_ftp)
        return True
    except Exception as e:
        print(e)
        return False


def directory_exists(dir):
    global ftp
    filelist = []
    ftp.retrlines('LIST', filelist.append)
    # print(filelist)
    for f in filelist:
        if f.split()[-1] == dir and f.upper().startswith('D'):
            return True
    return False


def chdir(dir):
    global ftp
    if directory_exists(dir) is False:
        ftp.mkd(dir)
    ftp.cwd(dir)


# Image to FTP
def ftp_connection(img_name, img_array):
    try:
        connect()
        try:
            login()
            chdir("Weapon_Detection")  # Change Directory

            try:
                image_rgb = Image.fromarray(np.uint8(img_array)).convert('RGB')
                image_bytes = io.BytesIO() 
                image_rgb.save(image_bytes, format="png") 
                image_bytes.seek(0)
                
                # Store image to FTP Server
                ftp.storbinary("STOR " + img_name, image_bytes)
                ftp.quit()

                image_bytes.close()

                IMG = BASE_URL + img_name
                return str(IMG)

            except Exception as E:
                print(E)

        except Exception as E:
            print(E)

    except Exception as E:
        print(E)


# FTP Image URL
def ftp_image_url(img_array):
    # Image Name Based on Current Time and Random number.
    ran_number = random.getrandbits(25)
    time = datetime.datetime.now().today()
    date_time = time.strftime("%d%m%Y_%H%M%S")
    img_name = "Img" + str(date_time) + "_" + str(ran_number) + ".jpeg"
    image = ftp_connection(img_name, img_array)
    return image


def get_entities(list_of_pictures):

    #Lists of lists for outputs of all images in the list_of_pictures
    main_is_weapon_detected = []
    main_labels_list = []
    main_confidence_list = []
    main_ftp_url = []

    for pic in list_of_pictures:
        response = requests.get(pic)
        img = Image.open(io.BytesIO(response.content))
        arr = np.uint8(img)

        arr = cv2.resize(arr, (640, 640), cv2.INTER_AREA)
        image_bytes = cv2.imencode('.jpg', arr)[1].tobytes()  # numpy to bytes
        files = {'image_path': image_bytes}
        response = requests.post(weapon_post_url, files=files)  # send image as bytes with request

        labels_list = response.json()["label"]
        confidence_list = response.json()["confidence"]
        bbox_list = response.json()["bbox"]
        image = arr

        if len(labels_list) == 0:
            is_weapon_detected = "False"
            ftp_url = ""

        else:

            is_weapon_detected = "True"
            for i in range(0, len(labels_list)):
                label = labels_list[i]
                confidence = confidence_list[i]
                bbox = bbox_list[i]

                print(label, confidence, bbox)
                x = int(bbox[0])
                y = int(bbox[1])
                w = int(bbox[2])
                h = int(bbox[3])
                label = response.json()["label"][0]

                image = cv2.resize(image, (640, 640), cv2.INTER_AREA)

                cv2.rectangle(image, (x, y), (w, h), (0, 0, 255), 3)
                annotated_image = cv2.putText(image, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 2)
            ftp_url = ftp_image_url(annotated_image)

        main_is_weapon_detected.append(is_weapon_detected)
        main_labels_list.append(labels_list)
        main_confidence_list.append(confidence_list)
        main_ftp_url.append(ftp_url)

    value = {
        "is_weapon_detected": main_is_weapon_detected,
        "predictions": main_labels_list,
        "confidence": main_confidence_list,
        "urls": main_ftp_url
    }

    # Dictionary to JSON Object using dumps() method
    # Return JSON Object
    return json.dumps(value)



# image_link = ['http://10.100.102.114/osint_system/media_files/TestImages/gun1.jpg', \
#         'http://10.100.102.114/osint_system/media_files/TestImages/gun2.jpg', \
#         'http://10.100.102.114/osint_system/media_files/TestImages/gun3.jpg',\
#         'http://10.100.102.114/osint_system/media_files/TestImages/gun4.jpg',]


image_link = ['http://10.100.102.114/osint_system/media_files/TestImages/gun4.jpg',]


final_response = get_entities(image_link)
print(final_response)