
from deeppavlov import configs, build_model
import numpy as np
import io
from io import BytesIO
from urllib.request import urlopen

import logging
logger = logging.getLogger(__name__)
if (logger.hasHandlers()):
    logger.handlers.clear()
logging.basicConfig(filename = "app.log", level = logging.DEBUG)


class DeeppavlovApp:

    def __init__(self):
        self.model = build_model(configs.nemo.asr)


    def get_model(self):
        return self.model

    def predict(self, input_url):
        # if  type(input_data) == io.BytesIO:
        try:
            memoryBuff = BytesIO(urlopen(input_url).read())
            text_batch = self.model([memoryBuff])
            return {"data": text_batch}
        except Exception as E:
            logging.error("Error 500: Internal Server Error : %s", str(E))
            return str(E), 500
    