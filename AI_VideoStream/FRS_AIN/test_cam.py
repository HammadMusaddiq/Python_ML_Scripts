from threading import Thread
import cv2, time

class ThreadedCamera(object):
    def __init__(self, src=0):
        self.capture = cv2.VideoCapture(src)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)
       
        # FPS = 1/X
        # X = desired FPS
        self.FPS = 1/30
        self.FPS_MS = int(self.FPS * 1000)
        
        # Start frame retrieval thread
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        
    def update(self):
        while True:
            if self.capture.isOpened():
                (self.status, self.frame) = self.capture.read()
            time.sleep(self.FPS)
            
    def show_frame(self):
        # cv2.imshow('frame', self.frame)
        # cv2.waitKey(self.FPS_MS)

        # cv2.namedWindow("Resized_Window", cv2.WINDOW_NORMAL)
        # # Using resizeWindow()
        # cv2.resizeWindow("Resized_Window", 1400, 800) # (w,h)
        # Displaying the image
        cv2.imshow("Resized_Window", self.frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.close_feed()
    
    def close_feed(self):
        self.capture.release()
        cv2.destroyAllWindows()
        

if __name__ == '__main__':
    # src = 'https://videos3.earthcam.com/fecnetwork/9974.flv/chunklist_w1421640637.m3u8'
    camera_user = "admin"
    camera_pass = "Admin12345"
    camera_ip = "192.168.23.199"

    src = "rtsp://"+camera_user+":"+camera_pass+"@"+camera_ip  # CCTV Camera (Dahua)

    threaded_camera = ThreadedCamera(src)
    while True:
        try:
            threaded_camera.show_frame()
        except AttributeError:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
            else:
                pass