from flask import Flask
from flask import request
from models.DeeppavlovApp import DeeppavlovApp
from deeppavlov import configs, build_model
from pydub import AudioSegment
import os
import json
import time

import logging
logger = logging.getLogger(__name__)
if (logger.hasHandlers()):
    logger.handlers.clear()
logging.basicConfig(filename = "app.log", level = logging.DEBUG)


app = Flask('TRANSCRIPTION')


transcription_model = DeeppavlovApp()



@app.route("/",methods=['POST'])
def transcription():
    if request.method == "POST":
        input_url = request.json["audio"]    
        if type(input_url)!= str:
            logging.error("Error 400: Bad Input")
            return "Error 400: Bad Input", 400
        else:
            start_time = time.time()
            output = transcription_model.predict(input_url)
            print("Time taken for transcription: ", time.time()-start_time)
            return output
    else:
        logging.error("Error 405: Method Not Allowed")
        return "Error 405: Method Not Allowed", 405


if __name__ == "__main__":
    app.run(debug=True)
