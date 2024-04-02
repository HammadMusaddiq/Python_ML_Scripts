import cv2
import aiRequests
import multiprocessing
from multiprocessing import Process
import boxPlot
import numpy as np


plot = boxPlot.Plot()
req = aiRequests.aiRequests()
manager = multiprocessing.Manager()


class Generate_frames:
    ip = "rtsp://admin:Admin12345@192.168.23.199"
    vid = cv2.VideoCapture(ip, cv2.CAP_FFMPEG)



    def gen_frames(self):
        counter = 0
         
        while self.vid.isOpened():
            success, frame = self.vid.read()  # read the camera frame
            manager = multiprocessing.Manager()
            return_dict = manager.dict()
            
            
            if not success:
                break
            else:
                if counter%25==0:
                    counter=0
                    files=self.create_request_args(frame)
                    try:
                        proc=Process(target=req.smoke_detection,args=(files,return_dict,))
                        proc.start()
                        proc1=Process(target=req.weapon_detection,args=(files,return_dict,))
                        proc1.start()
                        proc2=Process(target=req.frs_detection,args=(files,return_dict,))       
                        proc2.start()

                        proc.join()
                        proc1.join()
                        proc2.join()

                        print(return_dict)
                    except Exception as e:
                        import traceback
                        print(traceback.print_exc())
                        print('Exception in request  ::  ',e)
                
                counter +=1    
                
                # cv2.imshow('VIDEO', frame)
                # if cv2.waitKey(1) == ord('q'):
                try:
                    frame = plot.frs_plot(return_dict, frame)
                except:
                    pass
                try: 
                    frame = plot.weapons_plot(return_dict, frame)
                except:
                    pass 
                try:
                    frame = plot.smoke_det(return_dict, frame)
                except:
                    pass    
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n') 
    

    def create_request_args(self, frame):
        image = cv2.imencode('.jpg', frame)[1].tobytes()
        
        return {'image_path': image}

    

