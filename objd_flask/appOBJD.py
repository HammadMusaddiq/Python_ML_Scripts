from flask import Flask
from flask import request
from models.Detectron2App import Detectron2App

app = Flask('OBJD')
model = Detectron2App()

@app.route("/",methods=['POST'])
def objd():

    if request.method == "POST":
        image_url = request.json["imageUrl"]
        return model.predict(image_url)
    else:
        return "Error 405: Method Not Allowed"

@app.route("/get_config",methods=['GET'])
def getConfig():

    if request.method == "GET":
        return {"config":model.getConf()}
    else:
        return "Error 405: Method Not Allowed"
if __name__ == "__main__":
    app.run(debug=True)