from tkinter.tix import Tree
from deepface import DeepFace 
import requests
from PIL import Image
from deepface.commons import functions
from io import BytesIO
import numpy as np
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
        self.detector = MTCNN()

    def getModel(self):
        return self.model

    def getDetector(self):
        return self.detector

    def transformImage(self, image_bytes):
        # response = requests.get(image_bytes)
        # img = Image.open(BytesIO(image_bytes))
        img = Image.open(image_bytes)
        arr = np.uint8(img)
    
        image_shape = arr.shape
        # print("Image url shape: " + str(image_shape))
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

    def predict(self, image_bytes):
        logger.info("Detecting face in Image for extracting embeddings.")
        try:
            # import pdb; pdb.set_trace()
            if str(type(image_bytes)) != "<class 'numpy.ndarray'>":
                image_array = self.transformImage(image_bytes)
            
            image_array = image_bytes
            logger.info("Input Image Shape: " + str(image_array.shape))

            if image_array.shape[0]<400 and image_array.shape[1]<400:
                logger.info("Low Image Resolution, process exiting.")
                return {"data": 'Image Resolution is Low', "box": ''}

            face_results = self.detect_face(image_array)
            if face_results == []:
                logger.info("No face found in the image, process exiting.")
                return {"data": [], "box": ''}

            box_list = []
            embedding_list = []
            face_cnt = 0
            for _face in face_results:
                if _face['confidence'] > 0.95:
                    # extract the bounding box of face
                    x1, y1, width, height = _face['box']
                    # bug fix
                    x1, y1 = abs(x1), abs(y1)
                    x2, y2 = x1 + width, y1 + height
                    # extract the face
                    face = image_array[y1:y2, x1:x2]

                    face_cnt += 1
                    face_box = _face['box']

                    try:
                        target_img = functions.preprocess_face(face, target_size=(160, 160),\
                                enforce_detection=True, detector_backend='mtcnn')
                        
                        # if face extracted, then use this same face for resizing image and extracting embeddings (no black borders)
                        image = Image.fromarray(face)
                        image = image.resize((160, 160))
                        face_array = asarray(image)
                        
                        target_embedding = self.get_embedding(face_array)
                        embedding_list.append(target_embedding)    
                        box_list.append(_face['box'])

                    except:
                        continue


            # if embedding_list == [] and len(face_results) == 1:
            if embedding_list == [] and face_cnt == 1:             
                # if no face found in an image (where main model detected only single image), Input full image for DeppFace Preprocessing
                try:
                    target_img = functions.preprocess_face(image_array, target_size=(160, 160),\
                        enforce_detection=True, detector_backend='mtcnn')
                    
                    image = Image.fromarray(face)
                    image = image.resize((160, 160))
                    face_array = asarray(image)

                    target_embedding = self.get_embedding(face_array)
                    embedding_list.append(target_embedding)
                    box_list.append(face_box) 

                except:
                    pass

            logger.info("Number of faces after performing DeepFace Model processing: " + str(len(embedding_list)))

            if embedding_list == []:
                logger.info("No face in the processed image, process exiting.")    
            else:    
                logger.info("Face embeddings has been extracted.")

            return {"data": embedding_list, "box": box_list}

        except Exception as e:
            error = "An Exception Occured while extracting embeddings: {}".format(e)
            logger.error(error)
            return {"data": "", "box": ""}