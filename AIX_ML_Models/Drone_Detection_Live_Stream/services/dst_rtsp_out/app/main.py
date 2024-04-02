import subprocess
from flask import Response, Flask, render_template, request, redirect, url_for
import threading
import argparse
import time
import cv2
from pathlib import Path
import logging
import numpy as np

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s: PID %(process)d: %(message)s"
)
logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")

outputFrame = None
already_running = False
cap = None
DST_PROC = None

RTSP_STREAM_WAIT = 10

lock = threading.Lock()


# initialize a flask object
app = Flask(__name__,
            static_url_path='',
            static_folder='/app/static')


def test_camera_stream(cam_url):
    print(f"Checking camera RTSP for camera: {cam_url}...")
    time_check = time.time() + RTSP_STREAM_WAIT
    cap = cv2.VideoCapture(cam_url)
    while time.time() < time_check:
        success, frame = cap.read()
        if success:
            print(f"Camera stream is ok")
            return True
        else:
            print(f"Camera stream is not ok")
            print(f"Trying again till {time_check} secs...")
            time.sleep(5)
    return False


@app.route("/dst_app_starter", methods=["POST"])
def dst_app_starter():
    # return the rendered template
    if request.method == "POST":
        cam_url = request.form.get("camera_url", "")
        if test_camera_stream(cam_url):
            initialize_dst_app(cam_url=cam_url)
            return redirect(url_for("index"))
            # return render_template("index.html", msg="Camera RTSP working")
        else:
            return render_template("index.html", msg="Camera RTSP not working")


def initialize_dst_app(cam_url):
    global cap, already_running, DST_PROC
    already_running = True

    if DST_PROC:
        DST_PROC.kill()
        time.sleep(2.0)

    logs_file = open("logs.txt", "w")
    dst_file_path = Path("/app/dst_app.py")
    logging.info(f"Starting dst_app.py with camera url: {cam_url}")
    DST_PROC = subprocess.Popen(
        ["python3", dst_file_path, "-i", cam_url], shell=False, stdout=logs_file
    )
    time.sleep(2.0)

    source = "rtsp://localhost:8554/ds-test"
    cap = cv2.VideoCapture(source)
    time.sleep(2.0)


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


def generate():
    # grab global references to the output frame and lock variables
    global outputFrame, lock

    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if outputFrame is None:
                continue

            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

            # ensure the frame was successfully encoded
            if not flag:
                continue

        # yield the output frame in the byte format
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            bytearray(encodedImage) + b"\r\n"
        )


@app.route("/video_feed")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


def dst_app_thread():
    global cap, outputFrame
    while True:
        if cap:
            if cap.isOpened():
                ret_val, frame = cap.read()
                if frame is None:
                    outputFrame = np.zeros((360, 640, 3), np.uint8)
                elif frame.shape:
                    frame = cv2.resize(frame, (640, 360))
                    with lock:
                        outputFrame = frame.copy()
                else:
                    continue
        else:
            outputFrame = np.zeros((360, 640, 3), np.uint8)
            # print("camera open failed")


if __name__ == "__main__":
    # construct the argument parser and parse command line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-i",
        "--ip",
        type=str,
        required=False,
        default="192.168.2.226",
        help="ip address of the device",
    )
    ap.add_argument(
        "-o",
        "--port",
        type=int,
        required=False,
        default=9090,
        help="ephemeral port number of the server (1024 to 65535)",
    )
    ap.add_argument(
        "-f",
        "--frame-count",
        type=int,
        default=32,
        help="# of frames used to construct the background model",
    )
    args = vars(ap.parse_args())

    t = threading.Thread(target=dst_app_thread)
    t.daemon = True
    t.start()

    # start the flask app
    app.run(
        # host=args["ip"],
        host="0.0.0.0",
        port=args["port"],
        debug=True,
        threaded=True,
        use_reloader=False,
    )
