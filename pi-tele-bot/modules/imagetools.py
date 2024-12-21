import cv2
import numpy as np
import os

method = cv2.TM_CCOEFF_NORMED

def find_contrast():
   img = cv2.imread('./data/finder.png')
      #  constants
   BINARY_THRESHOLD = 5
   CONNECTIVITY = 10
   DRAW_CIRCLE_RADIUS = 4

   #  convert to gray
   gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

   #  extract edges
   binary_image = cv2.Laplacian(gray_image, cv2.CV_8UC1)

   #  fill in the holes between edges with dilation
   dilated_image = cv2.dilate(binary_image, np.ones((5, 5)))

   #  threshold the black/ non-black areas
   _, thresh = cv2.threshold(dilated_image, BINARY_THRESHOLD, 255, cv2.THRESH_BINARY)

   #  find connected components
   components = cv2.connectedComponentsWithStats(thresh, CONNECTIVITY, cv2.CV_32S)

   #  draw circles around center of components
   #see connectedComponentsWithStats function for attributes of components variable
   centers = components[3]
   for center in centers:
      cv2.circle(thresh, (int(center[0]), int(center[1])), DRAW_CIRCLE_RADIUS, (255), thickness=-1)

   cv2.imwrite("res.png", thresh)
   cv2.imshow("result", thresh)
   cv2.waitKey(0)

def check_dismiss_login():
   to_check = "./data/tmp.png"
   
   img = cv2.imread(to_check,1)
   template = cv2.imread('./data/dismiss-login.png',0)
   
   gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


   matched = cv2.matchTemplate(gray,template,cv2.TM_CCOEFF_NORMED)
   threshold = 0.9

   loc = np.where( matched >= threshold)
   data = list(zip(*loc[::-1]))
   print(data)
   # os.remove(to_check)
   if len(data) > 0:
      return True
   return False


def match_template() -> bool:
   to_check = "./data/tmp.png"
   
   img = cv2.imread(to_check,1)
   template = cv2.imread('./data/invalid.png',0)
   
   gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


   matched = cv2.matchTemplate(gray,template,cv2.TM_CCOEFF_NORMED)
   threshold = 0.9

   loc = np.where( matched >= threshold)
   data = list(zip(*loc[::-1]))
   os.remove(to_check)
   if len(data) > 0:
      return True
   return False
   # for pt in zip(*loc[::-1]):
   #    cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (255,0,0), 2)
   
   # cv2.imshow('Matched with Template',img)
   # cv2.waitKey(0)
   # # Read the images from the file
   # small_image = cv2.imread('data/invalid.png')
   # large_image = cv2.imread(f'data/tmp{idx}.png')
   # result = cv2.matchTemplate(small_image, large_image, method)
   # # We want the minimum squared difference
   # _,_,mnLoc,_ = cv2.minMaxLoc(result)
   # LPy,LPx = large_image.shape[:2]
   # # Draw the rectangle:
   # # Extract the coordinates of our best match
   # MPx,MPy = mnLoc
   
   
   # ValX = MPx / (LPx/4)
   # ValY = MPy / (LPy/2)
   
   # # if ValY > 0.9 and ValY < 1.2 and ValX > 0.9 and ValX < 1.2:
   # #    return True
   # # return False
   # # Step 2: Get the size of the template. This is the same size as the match.
   # trows,tcols = small_image.shape[:2]
   # # Step 3: Draw the rectangle on large_image
   # cv2.rectangle(large_image, (MPx,MPy),(MPx+tcols,MPy+trows),(0,0,255),2)

   # # Display the original image with the rectangle around the match.
   # cv2.imshow('output',large_image)

   # The image is only displayed if we call this
   # cv2.waitKey(0)
   
# find_contrast()