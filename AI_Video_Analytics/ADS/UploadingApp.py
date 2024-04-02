import os
import logging
import datetime
import logging
import urllib
import urllib.error
from FtpApp import FtpApp

logger = logging.getLogger(__name__)
if (logger.hasHandlers()):
    logger.handlers.clear()
logging.basicConfig(filename = "app.log", level = logging.DEBUG)

class UploadingApp:

    def __init__(self):

        self.ftp = FtpApp()
        self.ftp_cursor = self.ftp.getFTP()
        self.node_ip = self.ftp.node_ip_ftp
        self.audio_ftp_url = None

        self.base_url = "http://"+self.node_ip+"/osint_system/media_files/Audio_Downloads/"

    def set_audio_ftp_url(self,audio_name):
        """
        @return String  
        """
        self.audio_ftp_url = self.base_url + str(audio_name)+".mp3"
        return self.audio_ftp_url

    def get_audio_ftp_url(self):
        """
        @return String 
        """
        return self.audio_ftp_url

    
    # Audio Download
    def AudioDownload(self, audio_url, audio_name):
        output_filename = "TempAudioDir/"+audio_name+".mp3"
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers={'User-Agent':user_agent} 
        ext = audio_url.split('.')[-1]

        if ext == 'mp3':
            try:
                logging.info("Downloading started : {}".format(audio_url))
                request=urllib.request.Request(url = audio_url, headers = headers) 
                response = urllib.request.urlopen(request)
                open(output_filename, "wb").write(response.read())
            
                logging.info("Audio Downloaded: {}".format(audio_url))
                return True

            except urllib.error.HTTPError as e:
                logging.error("Internet Unavailable {}, output: {}".format(audio_url, e.__dict__))
                return False

            except urllib.error.URLError as e:
                logging.error("Wrong Url Error {}, output: {}".format(audio_url, e.__dict__))
                return False

        else:
            logging.error("Invalid Audio Url: {}".format(audio_url))
            return False


    # Audio to FTP
    def audioToFTP(self, url, audio_name):
        
        logging.info('Started')
        self.ctime = str(datetime.datetime.now())
        logging.info("Time: "+str(self.ctime))

        # Create Temp Dir
        if os.path.isdir("TempAudioDir") == False:
            os.mkdir("TempAudioDir")
            os.chmod("TempAudioDir",0o777)

        # Download Audio before accessign FTP, to overcome FTP timeout error
        audio_check = self.AudioDownload(url, audio_name)
                
        if audio_check == True:
            audio_filename = "TempAudioDir/"+audio_name+".mp3"
            
            if not self.ftp.is_connected():
                self.ftp.retry_ftp_connection()
            try:
                
                audio_ftp_url = self.get_audio_ftp_url()

                logging.info("Saving {} to FTP ".format(audio_filename))
                file = open(audio_filename,'rb')   # "rb" (reading the local file in binary mode)
                self.ftp_cursor.storbinary("STOR " + audio_name + ".mp3", file)
                self.ftp_cursor.quit()
                file.close()            
                logging.info("Audio URL: "+str(url))
                logging.info("Audio saved on Ftp URL: "+str(audio_ftp_url))
                logging.info('Finished with success')

                os.remove("TempAudioDir/"+audio_name+".mp3")
                return audio_ftp_url

            except Exception as E:
                os.remove("TempAudioDir/"+audio_name+".mp3")
                logging.error("something went wrong... Reason: {}".format(E))
                return False
                
        else:
            # Internet Disconnected
            logging.error("something went wrong")
            logging.error(str(url)) # here it will ge getting error 
            logging.error("Audio URL: "+str(url))
            logging.error('Finished with error(s)')
            return False

        

            