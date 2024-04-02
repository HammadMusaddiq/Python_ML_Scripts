from flask import Flask
from flask import request
from FtpApp import FtpApp
import os
from UTrimApp import UTrimApp
from datetime import datetime
import logging
from FtpApp import FtpApp
import json

logger = logging.getLogger(__name__)
if (logger.hasHandlers()):
    logger.handlers.clear()
logging.basicConfig(filename = "app.log", level = logging.DEBUG)


app = Flask('UTS_VIDEO')

@app.route("/",methods=['POST'])
def UTS_video():

    if request.method == "POST":
        payload = request.get_json(force=True)
        if 'video_url' not in payload:
            error = "Manadatory `video_url` parameter missing"
            logging.error(error)
            return error

        if 'video_name' not in payload:
            video_name = str(datetime.now().timestamp()).replace('.','')
            warning = "Missing `video_name` adding arbitrary name to video `{}.mp4`".format(video_name)
            logging.warn(warning)
        else:
            video_name = request.json['video_name']
        
        video_url = request.json["video_url"]
        video_start = request.json['video_start']
        video_end = request.json['video_end']

        downloader = UTrimApp(video_start=video_start,video_end=video_end)
        downloader.set_video_ftp_url(video_name)

        video_ftp_url = downloader.videoToFTP(video_url,video_name)
        
        if video_ftp_url != False:
            return {'url':video_ftp_url}
        else:
            return {'url':''}
    else:
        return "Error 405: Method Not Allowed"


if __name__ == "__main__":
    app.run(debug=True)