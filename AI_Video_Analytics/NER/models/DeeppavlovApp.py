from deeppavlov import configs, build_model
import numpy as np

import logging
logger = logging.getLogger(__name__)
if (logger.hasHandlers()):
    logger.handlers.clear()
logging.basicConfig(filename = "app.log", level = logging.DEBUG)


class DeeppavlovApp:

    def __init__(self):
        self.model = build_model(configs.ner.ner_ontonotes_bert_torch, download=True)


    def get_model(self):
        return self.model

    def predict(self, text):
        docs = []
        if  len(text) > 0:
            try: 
                docs = self.model(text)
                return {"data": docs}

            except Exception as E:
                logging.error("Error 500: Internal Server Error : %s", str(E))
                return str(E), 500
            
    