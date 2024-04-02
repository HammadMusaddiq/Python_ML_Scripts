from flask import Flask
from flask import request
from models.DeeppavlovApp import DeeppavlovApp
from deeppavlov import configs, build_model

import json

import logging
logger = logging.getLogger(__name__)
if (logger.hasHandlers()):
    logger.handlers.clear()
logging.basicConfig(filename = "app.log", level = logging.DEBUG)


app = Flask('NER')
model = DeeppavlovApp()

@app.route("/",methods=['POST'])
def ner():
    if request.method == "POST":
        text = request.json["text"]  
        if text is None or text == "":
            return [[],[]]
        if type(text)!= list:
            logging.error("Error 400: Bad Input")
            return "Error 400: Bad Input", 400  
        else:
            return model.predict(text)
    else:
        logging.error("Error 405: Method Not Allowed")
        return "Error 405: Method Not Allowed", 405


if __name__ == "__main__":
    app.run(debug=True)
