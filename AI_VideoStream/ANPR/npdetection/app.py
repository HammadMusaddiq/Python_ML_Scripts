from distutils.log import debug
from flask import Flask
from flask import request
from NPDetectionApp import NPDetection
#from NPDetectionApp import NPDetection
import logging

logger = logging.getLogger(__name__)
if (logger.hasHandlers()):
    logger.handlers.clear()

formatter = logging.Formatter('%(asctime)s | %(name)s |  %(levelname)s | %(message)s')
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("app.log")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

logger.info("App started")

app = Flask('LNPD') # Licence Number Plate Detection
model = NPDetection()

@app.route("/",methods=['POST'])
def LNP_Detection():

    if request.method == "POST":
        payload = request.get_json(force=True)
        if 'imageUrl' not in payload:
            error = "Manadatory `imageUrl` parameter missing"
            logger.error(error)
            return error
        
        image_url = request.json["imageUrl"]
        print(image_url)
        licence_plate = model.plate_detection(image_url)
        return {'licence_plate':licence_plate}

    else:
        return "Error 405: Method Not Allowed"


if __name__ == "__main__":
    app.run(debug=True)