import requests
import cv2
from bdb import set_trace
from datetime import datetime

# helper = Helping_Class.Helping_Class()

class TestApi:

    def create_request_args(self, frame):
        image = cv2.imencode('.jpg', frame)[1].tobytes()
        return {'image_path': image}

    def send_request_mulhim1(self, frame):
        files = self.create_request_args(frame)
        res = requests.post('http://127.0.0.1:5000/insert', files = files)
        if res.status_code == 200:
            return_dict = res.json()
        else:
            return_dict = {}
        return return_dict

    

def main():
    test = TestApi()
    # import pdb;pdb.set_trace()
    # import os
    # images_list = os.listdir('test_images')
    # # img = cv2.imread('001.jpg')
    # for img_name in images_list[:1]:
    #     img = cv2.imread('test_images/'+str(img_name))
    #     # cv2.imshow('d', img)
    #     # cv2.waitKey(0)
    #     # tt=datetime.now()
    #     test.test_vehicle(img)
    #     # result_img = test.test_vehicle(img)
    #     # result_img = test.test_people(result_img)
    #     # cv2.imwrite('result_images/ocr'+str(img_name), result_img)
    #     # tt -= datetime.now()

    #     # cv2.imshow('Time Taken'+str(tt), result_img)
    img = cv2.imread('01.jpg')
    res=test.send_request_mulhim1(img)
    print(res)
    # cv2.destroyAllWindows()


if __name__=='__main__':
    main()