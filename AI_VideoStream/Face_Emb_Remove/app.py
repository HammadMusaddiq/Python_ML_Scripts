from flask import Flask
from flask import request
from milvus_stream import Milvus_Stream
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

app = Flask('FRS-Deletion')
milvus = Milvus_Stream()


@app.route("/",methods=['GET'])
def hello():
    return "Face Deletion app is Up and Running!" , 200
    
def callingMilvus(id):
    status = milvus.delete_data(id)
    if status:
        return {'Status': status}
    else:
        return {'Status' : "No Embeddings Found"}


@app.route("/delete",methods=['POST'])
def delete_embeddings():
    if request.method == "POST":
        logger.info("Face Detection Started!")
        try:
            # image = request.files['image_path'] # image in bytes Body Form Data (file)
            mil_id = request.files['milvus_id'] #id to delete from milvus list from data (files)
        except:
            try:
                # image = request.json['image_path'] # image_url from Body Raw Json
                mil_id = request.json['milvus_id'] # milvus id from Body Raw Json
            except:
                try:
                    # image = request.form['image_path'] # image_url from Body Form Data (text)
                    mil_id = request.form['milvus_id'] # milvus id from Body Form Data (text)
                except:
                        logger.error("Error 400: Bad Input")
                        return "Error 400: Bad Input", 400

        try:
            status = callingMilvus(mil_id)

            return status

        except Exception as E:
            error = "An Exception Occured: {}".format(E)
            logger.error(error)
            return error,500
                
    else:
        error = "Error 405: Method Not Allowed"
        logger.error(error)
        return error, 405


if __name__ == "__main__":
    app.run(debug=False)