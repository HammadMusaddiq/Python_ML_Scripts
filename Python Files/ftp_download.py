from ftp_connection import Ftp_Stream
from PIL import Image
import io
import numpy as np
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

logger.info("App started")

class Ftp_Save():
    def __init__(self):
        self.ftp_class = Ftp_Stream()
        self.base_url = self.ftp_class.getBaseURL()
        self.ftp_cursor = self.ftp_class.getFTP()

    # def imageToFTP(self,path, file_name, image_bytes):
    #     if str(type(image_bytes)) == "<class 'numpy.ndarray'>": # if image type is numpy array
    #         image = Image.fromarray(np.uint8(image_bytes)).convert('RGB')
    #         # image = Image.fromarray(np.uint8(image_bytes))

    #         image_bytes = io.BytesIO() 
    #         image.save(image_bytes, format="png") 
    #         image_bytes.seek(0)

    #     # logger.info('Uploading Image to FTP')
    #     if not self.ftp_class.is_connected():
    #         self.ftp_class.retry_ftp_connection()
    #         self.ftp_class.change_ftp_present_working_dir(path)
    #     else:
    #         self.ftp_class.change_ftp_present_working_dir(path)
        
    #     try:
    #         baseurl = self.base_url # ('str' object has no attribute 'copy')

    #         for p in path.split('/')[1:]:
    #             baseurl = baseurl + "/" + str(p) 
            
    #         ftp_file_url = baseurl +"/"+ file_name
            
    #         self.ftp_cursor.storbinary("STOR " + file_name , image_bytes)
    #         # ftp_cursor.quit()
            
    #         # logger.info("Image saved on Ftp URL: "+str(ftp_file_url))

    #         return ftp_file_url

    #     except Exception as E:
    #         # logger.error("something went wrong... Reason: {}".format(E))
    #         logger.error("Error in ftp upload: {}, {}: {}: {}".format(E, self.base_url, baseurl, ftp_file_url))
    #         return False  



    def directory_exists(self, dir):
        filelist = []
        self.ftp_cursor.retrlines('LIST', filelist.append)
        for f in filelist:
            if f.split()[-1] == dir and f.upper().startswith('D'):
                return True
        return False

    def chdir(self, dir):
        if self.directory_exists(dir) is False:
            self.ftp_cursor.mkd(dir)
        self.ftp_cursor.cwd(dir)


    def imageToFTP(self, path, file_name, image_bytes,index):
        if str(type(image_bytes)) == "<class 'numpy.ndarray'>": # if image type is numpy array
            image = Image.fromarray(np.uint8(image_bytes)).convert('RGB')

            image_bytes = io.BytesIO() 
            image.save(image_bytes, format="png") 
            image_bytes.seek(0)

        if not self.ftp_class.is_connected():
            self.ftp_class.retry_ftp_connection()

        try:
            for folder in path.split('/')[1:]:
                self.chdir(folder)

            data = self.ftp_cursor.storbinary("STOR " + file_name , image_bytes)
            self.ftp_cursor.cwd("/home/microcrawler")
            BASE_URL = f"http://10.100.150.105/microcrawler{path}/"
            FTP_image_path = BASE_URL + file_name
            
            if index%20==0:
                self.ftp_cursor.quit()

            return FTP_image_path
        except Exception as E:
            print(E)
            print(index)
            return False