import os
import logging
import datetime
from threading import local
import pandas as pd
import subprocess
import json
import logging
import requests
import urllib
import urllib.error
from FtpApp import FtpApp

logger = logging.getLogger(__name__)
if (logger.hasHandlers()):
    logger.handlers.clear()
logging.basicConfig(filename = "app.log", level = logging.DEBUG)

class UTrimApp:

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

    
    # Video Download
    def VideoDownload(self, video_url, video_name):
        output_filename = "TempVideoDir/"+video_name+".mp4"

        cmd = ['yt-dlp',video_url,'--external-downloader','aria2c',"-S","res,ext:mp4:m4a","--recode","mp4",'-o',output_filename]
        
        process = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        logging.info("Downloading started : {}".format(video_url))
        #process.wait()
        #process = await asyncio.create_subprocess_exec(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

        # Status
        logging.info("Started Downloading: {}, pid={}".format(video_url, process.pid))

        # Wait for the subprocess to finish
        stdout, stderr = process.communicate()
        download_state = True
        # Progress
        if process.returncode == 0:
            stdout = stdout.decode('utf-8').strip().replace('\n',' ')
            logging.info(
                "Done: {}, pid={}, output: {}".format(video_url, process.pid, stdout)
            )
            subprocess.Popen(["chmod", "777",output_filename])
            
            process.wait()
            
            return download_state

        else:
            download_state = False
            stderr = stderr.decode("utf-8").strip().replace('\n','') #converted to string
            if 'Could not send HEAD request ' in stderr:
                logging.error("Wrong Url Error {}, pid={}, output: {}".format(video_url, process.pid, stderr))
            elif 'gaierror' in stderr and 'Could not send HEAD request' not in stderr:
                logging.error("Internet Unavailable {}, pid={}, output: {}".format(video_url, process.pid, stderr))
            elif 'HTTP Error 404: Not Found' in stderr:
                logging.error("URL Unavailable Error {}, pid={}, output: {}".format(video_url, process.pid, stderr))
            else:
                #FailedTasks.save_to_json(video_url, video_name)
                logging.warn(
                    "Retrying URL: An Exception Occured: {}, pid={}, output: {}".format(video_url, process.pid, stderr)
                )
            return download_state

    # mp4 Video Download
    def mp4Download(self, video_url, video_name):
        
        output_filename = "TempVideoDir/"+video_name+".mp4"
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers={'User-Agent':user_agent} 

        try:
            logging.info("Downloading started : {}".format(video_url))
            request=urllib.request.Request(url = video_url, headers = headers) 
            response = urllib.request.urlopen(request)
            open(output_filename, "wb").write(response.read())
        
            logging.info("Video Downloaded: {}".format(video_url))
            return True

        except urllib.error.HTTPError as e:
            logging.error("Internet Unavailable {}, output: {}".format(video_url, e.__dict__))
            return False

        except urllib.error.URLError as e:
            logging.error("Wrong Url Error {}, output: {}".format(video_url, e.__dict__))
            return False

    # Video Trimming
    def videoTrimming(self, video_path,start_time,end_time,video_name):

        output_file = "TempVideoDir/"+"Trim"+video_name+".mp4"

        cmd = ["ffmpeg",'-i',video_path,'-ss',start_time,'-to',end_time,'-c:v','copy','-c:a','copy',output_file,'-y'] 

        process = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        process.wait()

        return output_file



    # Video to FTP
    def videoToFTP(self, url, video_name):
        
        print("STARTED")
        logging.info('Started')
        self.ctime = str(datetime.datetime.now())
        logging.info("Time: "+str(self.ctime))

        # Create Temp Dir
        if os.path.isdir("TempVideoDir") == False:
            os.mkdir("TempVideoDir")
            os.chmod("TempVideoDir",0o777)

        try:
            # if URL has mp4 extension and has '/' in the last
            if url[-1] == '/':
                url = url[:-1]
            
            ext = url.split('.')[-1]
            if ext == 'mp4':
                video_check = self.mp4Download(url, video_name)

            else:
                # Download buffering video 
                video_check = self.VideoDownload(url, video_name)

        except Exception as E:
            logging.error("something went wrong... Reason: {}".format(E))
                    
        if video_check == True:
            video_filename = "TempVideoDir/"+video_name+".mp4"
            trim_video_path = self.videoTrimming(video_filename,self.video_start,self.video_end,video_name)
            
            if not self.ftp.is_connected():
                self.ftp.retry_ftp_connection()
            try:
                video_ftp_url = self.get_video_ftp_url()
                
                logging.info("Saving {} to FTP ".format(trim_video_path))
                file = open(trim_video_path,'rb')   # "rb" (reading the local file in binary mode)
                self.ftp_cursor.storbinary("STOR " + video_name + ".mp4", file)
                self.ftp_cursor.quit()
                file.close()            
                logging.info("Video URL: "+str(url))
                logging.info("Video saved on Ftp URL: "+str(video_ftp_url))
                logging.info('Finished with success')

                os.remove("TempVideoDir/"+video_name+".mp4")
                os.remove("TempVideoDir/"+"Trim"+video_name+".mp4")
                return video_ftp_url

            except Exception as E:
                os.remove("TempVideoDir/"+video_name+".mp4")
                logging.error("something went wrong... Reason: {}".format(E))
                return False
                
        else:
            # Internet Disconnected
            logging.error("something went wrong")
            logging.error(str(url)) # here it will ge getting error 
            logging.error("Video URL: "+str(url))
            logging.error('Finished with error(s)')
            return False

        

            
