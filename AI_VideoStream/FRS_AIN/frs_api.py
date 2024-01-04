import requests
import cv2


def frs_detection(img,return_dict):
    # res=requests.post('http://10.100.103.201:6003/search',data=img.tobytes(),timeout=30)

    image = cv2.imencode('.jpg', img)[1].tobytes() # numpy to bytes
    files={'image_path': image}
    res = requests.post(f"http://{'10.100.103.201'}:{6003}/{'search'}",files=files) # send image as bytes with request

    if res.status_code==200:
        # data=res.json()
        return_dict['frs_data'] = res.json()
    else:
        # data='MS not Working'
        return_dict['frs_data'] = 'MS not Working'
    
    return return_dict

def plotAnnotation(img, return_dict):
    # img = cv2.resize(im, (640,640), cv2.INTER_AREA)
    d = return_dict.get('frs_data')
    boxes = d.get('recognized_boxes')
    for box in boxes:
        img = cv2.rectangle(img,(int(box[0]), int(box[1])),(int(box[2]), int(box[3])), (0,0,255), 3)
    return img

def writeImage(img):
    cv2.imwrite("FRS_Image.jpg", img)

def showImage(img):
    cv2.imshow("FRS_Image", img)
    cv2.waitKey(0)
    cv2.destoryAllWindows()


return_dict = {}
img = cv2.imread("/home/hammad/Downloads/savedImage.jpg")
# img = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)

return_dict = frs_detection(img, return_dict)

if return_dict['frs_data'] != 'MS not Working' or return_dict != {}:
    plotAnnotation(img, return_dict)
    writeImage(img)
    # showImage(img)


# nparr = np.fromstring(request.data, np.uint8)
# image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)