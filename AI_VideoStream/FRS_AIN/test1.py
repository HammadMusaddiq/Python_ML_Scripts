
import cv2

image = cv2.imread("/home/hammad/Downloads/WhatsApp Image 2022-09-13 at 10.32.57 AM.jpeg")
recognized_boxes = [[244, 252, 124, 167]]
missed_boxes = []
image_label = ['Hammad']






def plotAnnotation(recognized_boxes, missed_boxes, image_label, image):


    # plot annotation
    annotated_image = image
    if isinstance(image_label, str):
        image_label = [image_label]

    for box, label in zip(recognized_boxes,image_label):
        if label == []:
            label = "Unknown"
        annotated_image = cv2.rectangle(annotated_image, (box[0], box[1]), (box[2]+box[0], box[3]+box[1]), (255,0,0), 3) 
        annotated_image = cv2.putText(annotated_image, label, (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,0,0), 2)
    
    for mbox in missed_boxes:
        annotated_image = cv2.rectangle(annotated_image, (mbox[0], mbox[1]), (mbox[2]+mbox[0], mbox[3]+mbox[1]), (255,255,0), 3)
    
    return annotated_image


ann_image = plotAnnotation(recognized_boxes, missed_boxes, image_label, image)
print(ann_image.shape)

cv2.imshow("Image", ann_image)
cv2.waitKey(0)
cv2.destroyAllWindows()