from json import detect_encoding
from frs_stream import FRS_Stream
from milvus_stream import Milvus_Stream

import logging
import operator

logger = logging.getLogger(__name__)
if (logger.hasHandlers()):
    logger.handlers.clear()

formatter = logging.Formatter('%(asctime)s | %(name)s |  %(levelname)s | %(message)s')
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("app.log")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

model = FRS_Stream()
milvus = Milvus_Stream()

class FRS_App:

    def sortDict(self,result_dict):
        return sorted(result_dict, key=operator.itemgetter('distance'), reverse=False)

    def removeDuplicates(self, matched_image_dict):
        # import pdb; pdb.set_trace()
        # Remove duplicates based on a single key in dict
        K = "urls"
        memo = set()
        res = []
        for sub in matched_image_dict:
            # testing for already present value
            for each in sub[K]:
                if each not in memo:
                    res.append(sub)
                    
                    # adding in memo if new value
                    memo.add(each)
        
        return res


    def extractNames(self, images_list):
        names = []
        for lst in images_list:
            if lst == []:
                names.append([])
            else:
                url = lst[0]['urls']
                name = url[0].split('/')[-1]
                name = name.split('_')[1]
                name = name.split('.jpg')[0]
                names.append(name)
        return names


    def flatten(self, list_of_lists):
        if len(list_of_lists) == 0:
            return list_of_lists
        if isinstance(list_of_lists[0], list):
            return self.flatten(list_of_lists[0]) + self.flatten(list_of_lists[1:])
        return list_of_lists[:1] + self.flatten(list_of_lists[1:])


    def dataSearch(self, embeddings):
        matched_images = []
        image_list = None
        logger.info("Starting searching similar embeddings.")
        for emb in embeddings:
            image_list = milvus.search(emb)
            if image_list != False:
                matched_images.append(image_list)
        
        return matched_images, image_list


    def dataExtracting(self, embeddings):
        detected_person = []
        
        if embeddings == 'Image Resolution is Low':
            result = {"matched_images" : {},
                "detected_person" : detected_person,
                "error" : embeddings,
            }


        elif len(embeddings) != 0:
            matched_images, image_list = self.dataSearch(embeddings)
            detected_person = self.extractNames(matched_images)
            matched_images_flatten = self.flatten(matched_images)
            
            
            if matched_images_flatten: 
                result_dict = self.removeDuplicates(matched_images_flatten)
                sorted_dict = self.sortDict(result_dict)

                logger.info("Matched images has been extracted, process completed with success.")
                result = {"matched_images" : sorted_dict, 
                    "detected_person" : detected_person,
                    "error" : "",
                }
            
            elif matched_images_flatten == [] and image_list != False: # if no image matched
                logger.info("No matched image found, process completed with success.")
                
                result = {"matched_images" : {}, 
                    "detected_person" : detected_person,
                    "error" : "",
                }

            else: # returing false, means searching failed on milvus database 
                result = {"matched_images" : {}, 
                    "detected_person" : detected_person,
                    "error" : "Error in similar image searching.",
                }
                        
        
        else: # no face found
            if embeddings == False:
                Error = "Error in extracting embeddings."
            else:
                Error = ""    
            
            result = {"matched_images" : {}, 
                "detected_person" : detected_person,
                "error" : Error,
            }

        return result
    
    def dataStoring(self, embeddings, image_links): #Editted by ISRAR_AHMED

        try:
            if embeddings == 'Image Resolution is Low':
                return {"milvus_id": "Image Resolution is Low"}

            elif len(embeddings) != 0:
            
                # milvus_ids = []
                # box_axis = []

                logger.info("Starting inserting embeddings in the Milvus DB.")
                idx = milvus.insert(embeddings)
                # for emb,bx in box:
                #     idx = milvus.insert(emb)
                #     if idx:
                #         milvus_ids.append(idx)
                #         box_axis.append([int(val) for val in bx])
                
                if idx:
                    check = milvus.dumpToElasticSearch(idx,image_links)
                    if check == True:
                        logger.info("Milvus ID has been saved in ES, Process completed with success.")
                        return {"milvus_id":idx} # milvus ids of all extracted faces embeddings
                # return {"milvus_ids":idx}
                else: # returing false, means embeddings not saved on milvus database
                    return False

            else:
                return {"milvus_id": []}
        
        except Exception as E:
            error = "An Exception Occured: {}".format(E)
            logger.error(error)
            return False


    def frsProcessing(self, image):
        try:
            face_prediction = model.predict(image)
            embeddings = face_prediction['embeddings']
            detected_boxes = face_prediction['detected_boxes']            
            recognized_boxes = face_prediction['recognized_boxes']            
            return embeddings, detected_boxes, recognized_boxes            

        except Exception as E:
            error = "An Exception Occured: {}".format(E)
            logger.error(error)
            return False
        