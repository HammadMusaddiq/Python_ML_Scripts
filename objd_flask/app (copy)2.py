from flask import Flask
from flask import request

import cv2
from skimage import io
from models.load_models import load_model

from detectron2.data import MetadataCatalog

app = Flask('OBJD')
predictor, cfg = load_model()

# Object Detection Class Names
class_names = MetadataCatalog.get(cfg.DATASETS.TRAIN[0]).thing_classes

@app.route("/",methods=['GET'])
def hello():
    return "<p>Hello, To MLOPs, I see you :v!</p>"

@app.route("/",methods=['POST'])
def objd():

    if request.method == "POST":
        list_of_urls = request.json["imageUrl"]
        results = []
        for i in list_of_urls:
            img = io.imread(i)
            im = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            # Make Prediction
            output = predictor(im)

            # # Axis of Predicted Objects in Images
            pred_axis = output['instances'].pred_boxes.tensor.tolist()
            pred_axis_round = []
            for i in pred_axis:
                pred_axis_round.append(['%.5f' % x for x in i])
            
            # Predicted classes and Scores
            p_classes = output['instances'].pred_classes.tolist()
            p_scores = output['instances'].scores.tolist()
            
            # Prediction classes in current image
            p_class_names = list(map(lambda x: class_names[x], p_classes))
            p_scores_round = ['%.2f' % x for x in p_scores]

            results.append({"predicted_axis":pred_axis_round,"object_classified":p_class_names,"probability_score":p_scores_round})

        return {"data": results}
    else:
        return "Error 405: Method Not Allowed"


if __name__ == "__main__":
    app.run(debug=True)
