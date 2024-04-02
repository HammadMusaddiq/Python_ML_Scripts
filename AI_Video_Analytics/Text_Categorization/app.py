from flask import Flask,abort
from flask import request
from models.ZeroShotApp import ZeroShotApp

import json

import logging
logger = logging.getLogger(__name__)
if (logger.hasHandlers()):
    logger.handlers.clear()
logging.basicConfig(filename = "app.log", level = logging.DEBUG)

app = Flask('Categorization')
model = ZeroShotApp()


@app.route("/",methods=['POST'])
def cat():
    if request.method == "POST":
        target_text = request.json["text"]  

        if type(target_text) != str:
            logging.error("(target_text -> %s) , Error 400:Bad Input",target_text)
            return "Error 400: Bad Input",400    
        #elif type(candidate_labels) != list:
            #logging.error("(candidate_labels -> {} , Error 400:Bad Input)".format(candidate_labels))
            #return "Error 400: Bad Input",400   
        else:
            return model.predict(target_text)
    else:
        logging.error("Error 405: Method Not Allowed")
        return "Error 405: Method Not Allowed", 405
        


if __name__ == "__main__":
    app.run(debug=True)
