import numpy 
import cv2

img = cv2.imread("/home/hammad/Downloads/Images/IMG_2046.jpg")

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.medianBlur(gray, 5)
edges = cv2.adaptiveThreshold(gray, 255,cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)

color = cv2.bilateralFilter(img, 9,250, 250)
cartoon = cv2.bitwise_and(color, color, mask=edges)


cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Image", 1400, 800) # (w,h)
cv2.imshow("Image", img)
cv2.waitKey()


cv2.namedWindow("Edges", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Edges", 1400, 800) # (w,h)
cv2.imshow("Edges", edges)
cv2.waitKey()


cv2.namedWindow("Cartoon", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Cartoon", 1400, 800) # (w,h)
cv2.imshow("Cartoon", cartoon)
cv2.waitKey()
cv2.destroyAllWindows()

#cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9
