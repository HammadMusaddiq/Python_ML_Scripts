
import cv2
import random

img = cv2.imread("/home/hammad/Downloads/IMG_2201.jpg")

bbox = [[1016,707,781,1028],[999,689,777,1014]]

rgb = []
for i in range(len(bbox)):
  r = random.randint(0,255)
  g = random.randint(0,255)
  b = random.randint(0,255)
  rgb.append((r,g,b))

print(rgb)

i = 1
for box,color in zip(bbox,rgb):
    annotated_image = cv2.rectangle(img, (box[0], box[1]), (box[2]+box[0], box[3]+box[1]), color, 3)
    annotated_image = cv2.putText(annotated_image, str(i), (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 2, color, 4) 
    i += 1

print(annotated_image.shape)

cv2.namedWindow("Resized_Window", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Resized_Window", 1400, 800) # (w,h)
cv2.imshow("Resized_Window", annotated_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

