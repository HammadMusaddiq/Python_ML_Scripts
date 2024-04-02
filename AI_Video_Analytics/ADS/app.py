from flask import Flask
from flask import request
from UploadingApp import UploadingApp
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
if (logger.hasHandlers()):
    logger.handlers.clear()
logging.basicConfig(filename = "app.log", level = logging.DEBUG)


app = Flask('ADS') # Audio Download Service ADS

@app.route("/",methods=['POST'])
def ADS():

    if request.method == "POST":
        payload = request.get_json(force=True)
        if 'audio_url' not in payload:
            error = "Manadatory `audio_url` parameter missing"
            logging.error(error)
            return error

        if 'audio_name' not in payload:
            audio_name = str(datetime.now().timestamp()).replace('.','')
            warning = "Missing `audio_name` adding arbitrary name to audio `{}.mp3`".format(audio_name)
            logging.warning(warning)
        else:
            audio_name = request.json['audio_name']
        
        audio_url = request.json["audio_url"]

        downloader = UploadingApp()
        downloader.set_audio_ftp_url(audio_name)

        audio_ftp_url = downloader.audioToFTP(audio_url,audio_name)
        
        if audio_ftp_url != False:
            return {'url':audio_ftp_url}
        else:
            return {'url':''}
    else:
        return "Error 405: Method Not Allowed"


if __name__ == "__main__":
    app.run(debug=True)