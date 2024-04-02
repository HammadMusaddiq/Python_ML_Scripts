import cv2
import numpy as np
import Model
from flask import Flask, request
import io, requests
from PIL import Image


#os.environ['CUDA_VISIBLE_DEVICES'] = '0'

classes=['Clear', 'Fire/Smoke']
model = Model.Model()

app = Flask(__name__)

@app.route('/insert', methods=['POST'])
def main():

    try:
        image = request.files['image_path']
        frame = model.transform(image)
        frame=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    except:
        try:
            nparr = np.fromstring(request.data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        except:
            # print('Second Except')
            link =request.form['image_path']
            response = requests.get(link)
            img = Image.open(io.BytesIO(response.content))
            arr = np.uint8(img)
            frame=cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)
            # cv2.imshow('', frame)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
    

    pred = model.predict(frame)

    dat_dict = {'Label': classes[pred]}
    return dat_dict




if __name__ == "__main__":
    

    app.run(debug=True)
