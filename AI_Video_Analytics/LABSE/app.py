from flask import Flask
from flask import request
from models.LabseApp import LabseApp


import logging
logger = logging.getLogger(__name__)
if (logger.hasHandlers()):
    logger.handlers.clear()
logging.basicConfig(filename = "app.log", level = logging.DEBUG)

model = LabseApp()
app = Flask("LABSE")

@app.route('/',methods=['POST'])
def getEmbeddings():
    if request.method == "POST":
        try:
            sentences = request.get_json()['text']
        except Exception as E:
            error = "500 Internal Server: Unable to Get text field"
            logging.error(error)
            return error, 500
        try: 
            embeddings = model.predict(sentences)
            return {"data":embeddings}, 200
        except Exception as E:
            error = "500 An Exception Occured:  {}".format(E)
            logging.error(error)
            return error, 500 

            
    else:
        error = "405 Method not Allowed"
        logging.error(error)
        return error, 405

if __name__ == "__main__":
    app.run(debug=True)