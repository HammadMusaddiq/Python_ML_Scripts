import cv2
from datetime import datetime
import os

class Plot:
    '''Class with all the functions for plotting for different ai Operations'''
    # extract the bounding box of face


    def frs_plot(self,return_dict,im):
        '''Getting Data from Dictionary and ploting boxes on faces'''
        annotated_image = im
        d=return_dict.get('frs_data')
        #missed_boxes = d.get('missed_boxes')
        recognized_boxes=d.get('detected_faces')
        #image_label=d.get('matched_results')['detected_person']
        for box in recognized_boxes:
            color = (0,255,255)  #yellow
            annotated_image = cv2.rectangle(annotated_image, (box[0], box[1]), (box[2]+box[0], box[3]+box[1]), color, 3)
            #annotated_image = cv2.putText(annotated_image, label, (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 2, color, 2)
        # for mbox in missed_boxes:
        #     annotated_image = cv2.rectangle(annotated_image, (mbox[0], mbox[1]), (mbox[2]+mbox[0], mbox[3]+mbox[1]), (255,255,0), 3)
        return annotated_image

    def set_annot(self, orig_image, boxes): #res_image_shape (width, height)
        # import pdb;pdb.set_trace()

        true_boxes=[]
        o_w, o_h=orig_image.shape[0], orig_image.shape[1] #actual image width and height
        n_w, n_h = 640,640 #Yolo output image width and height
        for index, single_point in enumerate(boxes):
            if index%2==0:
                new_point = (o_h * single_point) / (n_h)
            else:
                new_point = (o_w * single_point) / (n_w)
            true_boxes.append(new_point)
        return true_boxes

    def weapons_plot(self,return_dict,ann_image):
        '''Getting Data from Dictionary and ploting boxes on weapons'''
        # import pdb;pdb.set_trace()
        weapon_d=return_dict.get('weapons_data')
        wepon_boxes = weapon_d.get('bbox')
        for box_list in wepon_boxes:
            tru_boxes=self.set_annot(ann_image,box_list)
            # for box1 in tru_boxes:
            ann_image = cv2.rectangle(ann_image,(int(tru_boxes[0]), int(tru_boxes[1])),(int(tru_boxes[2]), int(tru_boxes[3])), (0,0,255), 3)
        return ann_image


    def smoke_det(self,return_dict,ann_image):
        '''Getting Data from Dictionary and Writing Smoke detected on Image'''
        fire_d=return_dict.get('smoke_data')
        fire_label=fire_d.get('Label')
        if fire_label=='Fire/Smoke':
            im=cv2.putText(ann_image, 'Fire/Smoke Detected', (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
            return im
        return ann_image

    def ANPR_plot(self,return_dict,im):
        annotated_image = im
        d = return_dict.get('ANPR_data')
        person_data=d.get('personData')
        recognized_boxes=person_data.get('bbox')
        for box in recognized_boxes:
            annotated_image = cv2.rectangle(annotated_image,(int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (255,255,255), 3)
        return annotated_image


    def createVideo(self,image_list, image_shape, fps):
        current_timestamp = str(datetime.now().timestamp()).replace(".","")
        current_date = datetime.now().strftime('%Y%m%d')
        v_download_path = "Video_Download"
        v_complete_path = None

        if not os.path.exists(v_download_path):
            os.mkdir(v_download_path)

        if not os.path.exists(v_download_path+"/"+current_date):
            os.mkdir(v_download_path+"/"+current_date)

        if os.path.exists(v_download_path+"/"+current_date):    
            v_complete_path = v_download_path+"/"+current_date+"/"+current_timestamp+".avi"
        
            # frames to single video (How to make video from frames in custom fps and time duration)
            img_size = (image_shape[1],image_shape[0])
            # MP4V (mp4), mp4v, DIVX (avi), XVID
            out = cv2.VideoWriter(v_complete_path,cv2.VideoWriter_fourcc(*'DIVX'), int(fps), img_size)
            for i in range(len(image_list)):
                frame = cv2.cvtColor(image_list[i], cv2.COLOR_BGR2RGB)
                # out.write(image_list[i])
                out.write(frame)

            out.release()
            # logger.info("Video Downloaded on path " + str(v_complete_path))        