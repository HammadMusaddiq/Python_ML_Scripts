import os
import logging
import datetime
from threading import local
import pandas as pd
import subprocess
import json
import logging
import requests
from FtpApp import FtpApp

logger = logging.getLogger(__name__)
if (logger.hasHandlers()):
    logger.handlers.clear()
logging.basicConfig(filename = "app.log", level = logging.DEBUG)

class LTrimApp:

    def __init__(self,video_start,video_end):

        self.ftp = FtpApp()
        self.ftp_cursor = self.ftp.getFTP()
        self.node_ip = self.ftp.node_ip_ftp
        self.video_ftp_url = None

        self.video_start = video_start
        self.video_end = video_end

        self.base_url = "http://"+self.node_ip+"/osint_system/media_files/Trimmed_videos/"

    def set_video_ftp_url(self,video_name):
        """
        @return String  
        """
        self.video_ftp_url = self.base_url + str(video_name)+".mp4"
        return self.video_ftp_url

    def get_video_ftp_url(self):
        """
        @return String 
        """
        return self.video_ftp_url

    
    # Video Trimming
    def videoTrimming(self, video_path,start_time,end_time,video_name):

        output_file = "TempVideoDir/"+"Trim"+video_name+".mp4"

        cmd = ["ffmpeg",'-i',video_path,'-ss',start_time,'-to',end_time,'-c:v','copy','-c:a','copy',output_file,'-y'] 

        process = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        process.wait()

        return output_file


    # Video to FTP
    def videoToFTP(self, local_video_ftp_path, video_name):
        
        print("STARTED")
        logging.info('Started')
        self.ctime = str(datetime.datetime.now())
        logging.info("Time: "+str(self.ctime))

        # Create Temp Dir
        if os.path.isdir("TempVideoDir") == False:
            os.mkdir("TempVideoDir")
            os.chmod("TempVideoDir",0o777)

        trim_video_path = self.videoTrimming(local_video_ftp_path,self.video_start,self.video_end,video_name)
        
        if not self.ftp.is_connected():
            self.ftp.retry_ftp_connection()
        try:
            video_ftp_url = self.get_video_ftp_url()
            
            logging.info("Saving {} to FTP ".format(trim_video_path))
            file = open(trim_video_path,'rb')   # "rb" (reading the local file in binary mode)
            self.ftp_cursor.storbinary("STOR " + video_name + ".mp4", file)
            self.ftp_cursor.quit()
            file.close()            
            logging.info("Video URL: "+str(local_video_ftp_path))
            logging.info("Video saved on Ftp URL: "+str(video_ftp_url))
            logging.info('Finished with success')

            os.remove("TempVideoDir/"+"Trim"+video_name+".mp4")
            return video_ftp_url

        except Exception as E:
            logging.error("something went wrong... Reason: {}".format(E))
            return False
            
        

            