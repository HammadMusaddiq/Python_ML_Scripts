import cv2
from datetime import datetime
import os
import ftplib
import subprocess
from dotenv import load_dotenv


class Plot:
    """Class with all the functions for saving local video and ftp uploads"""

    def __init__(self):
        load_dotenv()
        self.ftp_url = os.getenv("ftp_url")
        self.ftp_username = os.getenv("ftp_username")
        self.ftp_password = os.getenv("ftp_password")
        self.path_for_url = os.getenv("ftp_path_for_url")
        self.ftp_driectory_path = os.getenv("ftp_driectory_path")

        # print(self.ftp_url)

    def createVideo(self, image_list, image_shape, fps):
        # import pdb

        # pdb.set_trace()
        current_timestamp = str(datetime.now().timestamp()).replace(".", "")
        current_date = datetime.now().strftime("%Y%m%d")
        # user = os.environ.get("USERNAME")gpu-ain
        # user = "gpu-ain"

        # v_download_path = f"home/{user}/Desktop/localvideo"
        v_download_path = "localvideo"
        final_folder = "final"
        v_complete_path = None

        if not os.path.exists(v_download_path):
            os.mkdir(v_download_path)

        if not os.path.exists(v_download_path + "/" + current_date):
            os.mkdir(v_download_path + "/" + current_date)

        if os.path.exists(v_download_path + "/" + current_date):
            v_complete_path = (
                v_download_path + "/" + current_date + "/" + current_timestamp + ".mp4"
            )

            # frames to single video (How to make video from frames in custom fps and time duration)
            img_size = (image_shape[1], image_shape[0])
            # MP4V (mp4), mp4v, DIVX (avi), XVID
            out = cv2.VideoWriter(
                v_complete_path, cv2.VideoWriter_fourcc(*"mp4v"), int(fps), img_size
            )
            for i in range(len(image_list)):
                # frame = cv2.cvtColor(image_list[i], cv2.COLOR_BGR2RGB)
                out.write(image_list[i])
                # out.write(frame)

            out.release()
            if not os.path.exists(
                v_download_path + "/" + current_date + "/" + final_folder
            ):
                os.mkdir(v_download_path + "/" + current_date + "/" + final_folder)

            if os.path.exists(
                v_download_path + "/" + current_date + "/" + final_folder
            ):
                updated_v_complete_path = (
                    v_download_path
                    + "/"
                    + current_date
                    + "/"
                    + final_folder
                    + "/"
                    + current_timestamp
                    + ".mp4"
                )

            subprocess.run(
                ["ffmpeg", "-i", v_complete_path, "-y", updated_v_complete_path]
            )
            return updated_v_complete_path, v_complete_path
            # logger.info("Video Downloaded on path " + str(v_complete_path))

    def videoToFTP(self, file_name, v_complete_path):  # store image on FTP
        # import pdb

        # pdb.set_trace()

        ftp = ftplib.FTP(self.ftp_url)
        try:
            ftp.login(self.ftp_username, self.ftp_password)
            ftp.cwd(self.ftp_driectory_path)
        except Exception as e:
            print(e)

        try:
            file = open(
                v_complete_path, "rb"
            )  # replace video.mp4 with your video file name
            ftp.storbinary(f"STOR {file_name}.mp4", file)
            ftp_file_url = (
                "http://" + self.ftp_url + "/" + self.path_for_url + file_name + ".mp4"
            )
            return ftp_file_url

        except Exception as E:
            print(E)
            return False
