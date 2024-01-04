import cv2
import requests
import base64
import numpy as np
from skimage import io

from pyspark.sql import SparkSession
from pyspark.sql import Row
from pyspark.sql.functions import udf
from pyspark.sql.types import StructType, StructField, StringType, BinaryType, ArrayType

from OwlsenseStream import OwlsenseStream

from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog, DatasetCatalog
from detectron2 import model_zoo

spark = SparkSession.builder.getOrCreate()

# Configuration of model
cfg = get_cfg()
model_file = "COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml"
cfg.merge_from_file(model_zoo.get_config_file(model_file))
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(model_file)
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.7
cfg.MODEL.DEVICE='cpu'

# Class Names
class_names = MetadataCatalog.get(cfg.DATASETS.TRAIN[0]).thing_classes

# Create predictor
predictor = DefaultPredictor(cfg)

schema_obj_detection = ArrayType(StructType([
        StructField('image_base64', StringType(), False),
        StructField('object_classified', ArrayType(StringType()), False),
        StructField('probability_score', ArrayType(StringType()), False)
    ]))


def object_detection(im,predictor,cfg):
    # Make Prediction
    output = predictor(im)
    # Make Visualization
    v = Visualizer(im[:, :, ::-1], MetadataCatalog.get(cfg.DATASETS.TRAIN[0]), scale=1.2)
    v = v.draw_instance_predictions(output["instances"].to("cpu"))
    im1 = v.get_image()[:, :, ::-1]
    # Base64 String
    # im2 = cv2_imshow(v.get_image()[:, :, ::-1])
    # im_arr: Numpy Array to one-dim array format.
    _, im_arr = cv2.imencode('.jpg', im1)  
    im_bytes = im_arr.tobytes()
    # image to Base64
    im_b64 = str(base64.b64encode(im_bytes))
    # Predicted classes and Scores
    pred_class = output['instances'].pred_classes.tolist()
    pred_score = output['instances'].scores.tolist()
    return im_b64, pred_class, pred_score


@udf(schema_obj_detection) 
def get_entities(list_of_urls):

    # image_base64 = []
    # object_classified = []
    # probability_score = []
    results = []
    for j in list_of_urls:
        for i in j:
            # print("\nCURRENT IMAGE URL:", i)           
            try:    
                # Read image from URL
                img = io.imread(i)
                try:
                    img1 = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                    img_b64, p_classes, p_scores = object_detection(img1, predictor, cfg)
                    # Prediction classes in current image
                    p_class_names = list(map(lambda x: class_names[x], p_classes))
                    p_scores_round = ['%.2f' % x for x in p_scores]

                    # print("String Length: ", len(img_b64)) 
                    # print("Predicted Classes: ", p_class_names)
                    # print("Predicted Scores: ", p_scores_round)
                    results.append({"image_base64":img_b64,"object_classified":p_class_names,"probability_score":p_scores_round})
                    # image_base64.append(img_b64)
                    # object_classified.append(p_class_names)
                    # probability_score.append(p_scores_round)

                except:
                    print("Error in fetching data.")
            except:
                    results.append({"image_base64":"","object_classified":[],"probability_score":[]})

                # print("Image URL is expired.") 
    return results
    # return Row('image_base64', 'object_classified', 'probability_score')\
    # (image_base64, object_classified, probability_score)


def callback(df):

    outputs_def = df.select("CTR", "GTR", "target_type", "target_subtype", "media_c" ,get_entities("media_c").alias("Object_Detection"))
    print(outputs_def.select("Object_Detection").show(truncate=False))

    #outputs_def.coalesce(1).write.format('json').save('new_data2.json')
    #df2 = outputs_def.toPandas()
    #df2.to_json (r'/home/hammad/VScodeProjects/Kafka_Screaming/Streamed_Data/new_data.json')

    return outputs_def

df = spark.read.format("json").option("inferSchema","true").option("multiline","true").load("/home/hammad/VScodeProjects/Kafka_Screaming/Streamed_Data/new_streamed_data.json")
callback(df)