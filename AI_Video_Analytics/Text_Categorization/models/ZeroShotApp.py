#Import Flask
from flask import json

#Import Libraries for your model
from transformers import pipeline
import string

import configparser
from pywebhdfs.webhdfs import PyWebHdfsClient

import logging
logger = logging.getLogger(__name__)
if (logger.hasHandlers()):
    logger.handlers.clear()
logging.basicConfig(filename = "app.log", level = logging.DEBUG)

# import os
# thisfolder = os.path.dirname(os.path.abspath("/Desktop/Arslan_Thaheem_data/api/Text_categorization_api (copy)/models"))
# initfile = os.path.join(thisfolder, 'config.ini')
import ast

class ZeroShotApp:

    def __init__(self):
        self.classifier = pipeline("zero-shot-classification",model="joeddav/xlm-roberta-large-xnli")
        self.local_config_parses = configparser.ConfigParser()
        self.local_config_parses.read("config.ini")

        self.cat_in = ast.literal_eval(self.local_config_parses['SAUDIARAB']['cat_in'])
        self.cat_out = ast.literal_eval(self.local_config_parses['SAUDIARAB']['cat_out'])


    def get_model(self):
        return self.classifier

    def predict(self, x):
        target_text = str(x)
        predictions = []
        confidence = []
        res = sum([i.strip(string.punctuation).isalpha() for i in target_text.split()])


        try:
            if res > 8:
        
               

                for lst_in,lst_out in zip(self.cat_in,self.cat_out):
                    # print(lst_in)
                    
                    result = self.classifier(target_text, lst_in)
                    label = result["labels"][0]
                    score = result["scores"][0]

                    if score > 0.6:

                        for val_1,val_2 in zip(lst_in,lst_out):

                            if val_1 == label:
                                if val_2 != "":
                                    predictions.append(val_2)
                                    confidence.append(score)
                                else:
                                    predictions.append(val_1)
                                    confidence.append(score)

                if not predictions:
                    predictions.append("Other")
                    confidence.append("0.0")  

            else:
                predictions.append("Insufficient Info")
                confidence.append("0.0")

            
 
            data = {"confidence": confidence, "predictions": predictions}
            return json.dumps(data)    
        except Exception as E:
            logging.error("Error 500:Internal Server Error")
            print(str(E))
            return str(E), 500



