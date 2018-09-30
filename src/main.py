# import the necessary packages
import numpy as np
import argparse
import imutils
import glob
import cv2
import os.path


t1 = 0
t2 = 255

my_path = os.path.abspath(os.path.dirname(__file__))
template_path = os.path.join(my_path, "../store_templates/Markham's_template.png")
image_path = os.path.join(my_path, "../test_images/Markham_saved.jpg")

template = cv2.imread(template_path)
template_grey = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

cv2.namedWindow("Trackbars")

def t1_cb(new_value):
    global t1, template
    t1 = new_value
    template = cv2.Canny(template_grey, t1, t2)
    cv2.imshow("Template", template)
def t2_cb(new_value):
    global t2, template
    t2 = new_value
    template = cv2.Canny(template_grey, t1, t2)
    cv2.imshow("Template", template)

tb_thresh1 = cv2.createTrackbar("thresh1", "Trackbars", t1, 255, t1_cb)
tb_thresh1 = cv2.createTrackbar("thresh2", "Trackbars", t2, 255, t2_cb)

cv2.waitKey(0)

# load the image image, convert it to grayscale, and detect edges

sources = [image_path]
(tH, tW) = template.shape[:2]

# loop over the images to find the template in
for imagePath in sources:
	# load the image, convert it to grayscale, and initialize the
	# bookkeeping variable to keep track of the matched region
	image = cv2.imread(imagePath)
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	found = None
 
	# loop over the scales of the image
	for scale in np.linspace(0.2, 1.0, 20)[::-1]:
		# resize the image according to the scale, and keep track
		# of the ratio of the resizing
		resized = imutils.resize(gray, width = int(gray.shape[1] * scale))
		r = gray.shape[1] / float(resized.shape[1])
 
		# if the resized image is smaller than the template, then break
		# from the loop
		if resized.shape[0] < tH or resized.shape[1] < tW:
			break

        # detect edges in the resized, grayscale image and apply template
		# matching to find the template in the image
		edged = cv2.Canny(resized, 50, 200)
		result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF)
		(_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)
 
        # check to see if the iteration should be visualized
        # draw a bounding box around the detected region
        clone = np.dstack([edged, edged, edged])
        cv2.rectangle(clone, (maxLoc[0], maxLoc[1]),
            (maxLoc[0] + tW, maxLoc[1] + tH), (0, 0, 255), 2)
        cv2.imshow("Visualize", clone)
        cv2.waitKey(0)
 
        # if we have found a new maximum correlation value, then ipdate
        # the bookkeeping variable
        if found is None or maxVal > found[0]:
            found = (maxVal, maxLoc, r)
 
	# unpack the bookkeeping varaible and compute the (x, y) coordinates
	# of the bounding box based on the resized ratio
	(_, maxLoc, r) = found
	(startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
	(endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))
 
	# draw a bounding box around the detected result and display the image
	cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
	cv2.imshow("Image", image)
	cv2.waitKey(0)