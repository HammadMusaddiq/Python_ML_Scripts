from deepface import DeepFace
import requests
from PIL import Image
from deepface.commons import functions
from io import BytesIO
import numpy as np
from retinaface import RetinaFace
from mtcnn.mtcnn import MTCNN
import logging

from numpy import asarray
from numpy import expand_dims

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
        self.model = DeepFace.build_model("Facenet")
        self.detector_r = RetinaFace

    def getModel(self):
        return self.model
    
    def getDetector(self):
        return self.detector_r

    def transformImage(self, image):
        try: # read image_url
            response = requests.get(image)
            img = Image.open(BytesIO(response.content))
        except: # read image_bytes
            try:
                img = Image.open(image)
            except:
                img = Image.open(BytesIO(image))

        arr = np.uint8(img)
    
        image_shape = arr.shape
        if image_shape[2] != 3: # convering image to 3 channels for extracting embeddings
            arr = arr[:,:,:3]
        return arr

    def detect_face(self,image_array):
        face_results = self.getDetector().detect_faces(image_array)
        logger.info("Number of faces found from Image: " +str(len(face_results)))
        return face_results

    def get_embedding(self, face_pixels):
        # scale pixel values
        face_pixels = face_pixels.astype('float32')
        # standardize pixel values across channels (global)
        mean, std = face_pixels.mean(), face_pixels.std()
        face_pixels = (face_pixels - mean) / std
        # transform face into one sample
        samples = expand_dims(face_pixels, axis=0)
        # make prediction to get embedding
        yhat = self.getModel().predict(samples)
        return yhat[0]

    def get_annotations(self, img):
        face_results = self.detect_face(img)
        return face_results
    
    def _embeddings(self, face):
        image = Image.fromarray(face)
        image = image.resize((160, 160))
        face_array = asarray(image)
        
        target_embedding = self.get_embedding(face_array)
        return target_embedding


    def predict(self, img):
        logger.info("Detecting face in Image for extracting embeddings.")
        try:
            if str(type(img)) != "<class 'numpy.ndarray'>":
                img = self.transformImage(img)

            logger.info("Input Image Shape: " + str(img.shape))

            embedding_list = []
            recognized_boxes = []

            if img.shape[0]<=160 and img.shape[1]<=160: # face image
                embedding_list.append(self._embeddings(img))
                recognized_boxes.append([0, 0, img.shape[0], img.shape[1]])
                return {"embeddings": embedding_list, "recognized_boxes": recognized_boxes}
                #face_results = {'face_1': {'facial_area': [0, 0, img.shape[0], img.shape[1]]}} # dict of face with bbox
            
            else:
                face_results = self.get_annotations(img)

                if face_results == []:
                    logger.info("No face found in the image, process exiting.")
                    return {"embeddings": [], "recognized_boxes": []}
                    
                _face_conf = None
                _face_box = None
                _model_name = None

                for _face in face_results:
                    try:
                        _face = face_results.get(_face)  # Retina Face
                        _face_conf = _face['score']
                        _face_box = _face['facial_area']
                        _face_box = [_face_box[0],_face_box[1],_face_box[2]-_face_box[0], _face_box[3]-_face_box[1]] # Bcz Facenet model takes boxes differently (mtcnn format)
                        _model_name = 'retinaface'
                    except:
                        try:
                            _face_conf = _face['confidence'] # MTCNN
                            _face_box = _face['box']
                            # _face_box = [_face_box[0],_face_box[1],_face_box[2]+_face_box[0], _face_box[3]+_face_box[1]] # now not need to do anything in ploting
                            _model_name = 'mtcnn'
                        except Exception:
                            logger.warn("Extracted face has no data.")    
                            continue
                    
                    if _face_conf > 0.95:
                        # extract the bounding box of face
                        x1, y1, width, height = _face_box
                        # bug fix
                        x1, y1 = abs(x1), abs(y1)
                        x2, y2 = x1 + width, y1 + height
                        # extract the face
                        face = img[y1:y2, x1:x2]


                        recognized_boxes.append(_face_box)
                        embedding_list.append(self._embeddings(face))

            
            logger.info("Number of faces after performing DeepFace Model processing: " + str(len(embedding_list)))

            if embedding_list == []:
                logger.info("No face in the processed image, process exiting.")    
            else:    
                logger.info("Face embeddings has been extracted.")

            return {"embeddings": embedding_list, "recognized_boxes": recognized_boxes}

        except Exception as e:
            error = "An Exception Occured while extracting embeddings: {}".format(e)
            logger.error(error)
            return {"embeddings": False, "recognized_boxes": []}
