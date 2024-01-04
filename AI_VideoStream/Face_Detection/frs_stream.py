from PIL import Image
from io import BytesIO
import numpy as np
from retinaface import RetinaFace
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

class FRS_Stream:

    def __init__(self):
        self.detector = RetinaFace

    def getDetector(self):
        return self.detector

    def transformImage(self, image_bytes):
        # response = requests.get(image_bytes)
        # img = Image.open(BytesIO(image_bytes))
        img = Image.open(image_bytes)
        arr = np.uint8(img)
    
        image_shape = arr.shape
        if image_shape[2] != 3: # convering image to 3 channels for extracting embeddings
            arr = arr[:,:,:3]
        return arr

    def detect_face(self,image_array):
        face_results = self.getDetector().detect_faces(image_array)
        logger.info("Number of faces found from Image: " +str(len(face_results)))
        return face_results

    def predict(self, img):
        logger.info("Detecting face in Image for extracting embeddings.")
        try:
            if str(type(img)) != "<class 'numpy.ndarray'>":
                img = self.transformImage(img)

            logger.info("Input Image Shape: " + str(img.shape))

            face_results = self.detect_face(img)
            if face_results == []:
                logger.info("No face found in the image, process exiting.")
                return {"detected_boxes": []}
                
            detected_boxes = []

            _face_conf = None
            _face_box = None

            for _face in face_results:
                try:
                    _face = face_results.get(_face)  # Retina Face
                    _face_conf = _face['score']
                    _face_box = _face['facial_area']
                    _face_box = [_face_box[0],_face_box[1],_face_box[2]-_face_box[0], _face_box[3]-_face_box[1]]
                except:
                    logger.warn("Extracted face has no data.")    
                    continue
                
                if _face_conf > 0.95:
                    detected_boxes.append(_face_box)


            logger.info("Face area has been extracted.")

            return {"detected_boxes": detected_boxes}

        except Exception as e:
            error = "An Exception Occured while extracting face area: {}".format(e)
            logger.error(error)
            return {"detected_boxes": []}
