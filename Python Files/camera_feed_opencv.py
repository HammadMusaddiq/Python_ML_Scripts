import cv2

camera_ip1 = "rtsp://admin:Rapidev@321@192.168.23.166"
camera_ip2 = "rtsp://admin:Rapidev@321@192.168.23.166:554/cam/realmonitor?channel=1&subtype=0"

camera_ip3 = "rtsp://admin:Admin12345@192.168.23.199"
camera_ip4 = "rtsp://admin:Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0"

camera_ip5 = "gstreamer_str='appsrc ! videoconvert ! x264enc tune=zerolatency bitrate=5000 speed-preset=superfast ! rtph264pay ! udpsink host=admin:Rapidev@321@192.168.23.166 port=554'"
camera_ip6 = "gstreamer_str='udpsrc port=554 ! application/x-rtp,encoding-name=(string)H264,payload=(int)96,clock-rate=(int)90000,media=(string)video ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! video/x-raw,format=(string)BGR ! videoconvert ! appsink name=sink emit-signals=true sync=false max-buffers=1 drop=true'"

camera_ip7 = "gst-launch-1.0 mfvideosrc device-index=0 ! video/x-raw,width=1280,height=720,framerate=30/1 ! videoscale ! videoconvert ! x264enc tune=zerolatency bitrate=5000 speed-preset=superfast ! rtph264pay config-interval=1 pt=96 ! udpsink host=admin:Rapidev@321@192.168.23.166 port=554"
camera_ip8 = "gst-launch-1.0 rtspsrc location=rtsp://admin:Rapidev@321@192.168.23.166:554/live/ch00_0 ! rtph264depay ! h264parse ! decodebin ! autovideosink"
camera_ip9 = "rtsp://admin:Rapidev@321@192.168.23.166:554/live/ch00_0"
camera_ip10 = "rtsp://admin:Rapidev@321@192.168.23.166:554"
camera_ip11 = "rtsp://admin:Rapidev@321@192.168.23.166:554/cam/realmonitor?channel=0&subtype=1"


camera_ip12 = "rtsp://admin:Rapidev321@192.168.23.166:554"
camera_ip13 = "admin://Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0"
camera_ip14 = "rtsp://Admin12345@192.168.23.199:554/cam/realmonitor?channel=1&subtype=0"

camera_ip12 = "rtsp://admin:Rapidev321@192.168.23.157:554"


drone_ip1 = "rtmp://192.168.25.79:1935"
drone_ip2 = "rtmp://192.168.25.79:1935/live/realmonitor?channel=1&subtype=0"
drone_ip3 = "rtsp://192.168.25.79:1935"

vid = cv2.VideoCapture(camera_ip12, cv2.CAP_FFMPEG)

counter = 0
frames_list = list()


def makeVideo(frames_list, fps, img_size):
    # mp4v -> (mp4) 
    # DIVX, XVID -> (avi)
    out = cv2.VideoWriter("live_stream_video.mp4",cv2.VideoWriter_fourcc(*'mp4v'), int(fps), img_size)
    for i in range(len(frames_list)):
        # frame = cv2.cvtColor(frames_list[i], cv2.COLOR_BGR2RGB)
        out.write(frames_list[i])
        # out.write(frame)
    out.release()


while vid.isOpened():   
    ret, frame = vid.read()

    # if frame is read correctly ret is True
    if not ret:
        pass
            
    else:

        if counter == 0:
            fps = vid.get(cv2.CAP_PROP_FPS)
            img_size = (frame.shape[1],frame.shape[0])
            cv2.imwrite("camera157.jpg", frame)
        
        counter = counter + 1
        frames_list.append(frame)

        if len(frames_list) >= 100:
            makeVideo(frames_list, fps, img_size)
            break

        # # Naming a window
        # cv2.namedWindow("Resized_Window", cv2.WINDOW_NORMAL)

        # # Using resizeWindow()
        # cv2.resizeWindow("Resized_Window", 1400, 800) # (w,h)

        # # Displaying the image
        # cv2.imshow("Resized_Window", frame)
        
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

vid.release()
cv2.destroyAllWindows() ## To destroy All shown frames