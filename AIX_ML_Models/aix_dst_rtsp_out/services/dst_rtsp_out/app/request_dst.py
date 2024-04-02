from flask import Response, Flask, render_template, request, redirect, url_for
import logging
import subprocess
from threading import Thread
from pathlib import Path
import time
import requests


logging.basicConfig(
    level=logging.INFO, format="%(levelname)s: PID %(process)d: %(message)s"
)
logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")


already_running = False
cap = None
DST_PROC = None


app = Flask(__name__)

@app.route("/dst_app_exit", methods=["POST"])
def dst_app_exit():
    try:
        cam_url = request.form.get('camera_url')
        cam_ip = request.form.get('camera_ip')
        kafka_ip = request.form.get('kafka_ip')
        
        global DST_PROC

        if DST_PROC:
            DST_PROC.kill()
            time.sleep(2.0)

        return {"stream_out" : "Stream Terminated", "Error": False}

    except Exception as E:
        return {"stream_out" : False, "Error": str(E)}

@app.route("/dst_app_starter", methods=["POST"])
def dst_app_starter():
    try:
        cam_url = request.form.get('camera_url')
        cam_ip = request.form.get('camera_ip')
        kafka_ip = request.form.get('kafka_ip')
        Thread(target = initialize_dst_app, args = (cam_url,cam_ip,kafka_ip,)).start()
        return {"stream_url" : "rtsp://{}:8553/ds-aix-1".format("10.100.160.103")}

    except Exception as E:
        return {"stream_url" : str(request.form)}



def initialize_dst_app(cam_url, cam_ip, kafka_ip):
    global cap, already_running, DST_PROC
    already_running = True

    if DST_PROC:
        DST_PROC.kill()
        time.sleep(2.0)

    logs_file = open("logs.txt", "w")
    dst_file_path = Path("/app/dst_app.py")
    logging.info(f"Starting dst_app.py with camera url: {cam_url}")

    DST_PROC = subprocess.Popen(
        ["python3", dst_file_path, "-i", cam_url, "-p", cam_ip, "-k", kafka_ip], shell=False, stdout=logs_file
    )


if __name__ == "__main__":
    app.run(
        # host=args["ip"],
        host="0.0.0.0",
        port=8005,
        debug=True,
        threaded=True,
        use_reloader=False,
    )
        