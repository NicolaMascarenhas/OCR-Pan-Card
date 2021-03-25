# import necessary packages
from PIL import Image
import pytesseract
import argparse
import cv2
import os
import re
import io
import json
import ftfy

import datefinder

######  Initiate the command line interface

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,help="path to input image to be OCR'd")
ap.add_argument("-p", "--preprocess", type=str, default="thresh",help="type of preprocessing to be done, choose from blur, linear, cubic or bilateral")
args = vars(ap.parse_args())


#####  Load & Preprocess image 

# load the example image and convert it to grayscale
image = cv2.imread(args["image"])
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# check to see if we should apply thresholding to preprocess the
# image
if args["preprocess"] == "thresh":
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

elif args["preprocess"] == "adaptive":
    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)

if args["preprocess"] == "linear":
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)

elif args["preprocess"] == "cubic":
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

# make a check to see if blurring should be done to remove noise, first is default median blurring

if args["preprocess"] == "blur":
    gray = cv2.medianBlur(gray, 3)

elif args["preprocess"] == "bilateral":
    gray = cv2.bilateralFilter(gray, 9, 75, 75)

elif args["preprocess"] == "gauss":
    gray = cv2.GaussianBlur(gray, (5,5), 0)

# write the grayscale image to disk as a temporary file so we can apply OCR to it
filename = "{}.png".format(os.getpid())
cv2.imwrite(filename, gray)

'''
A blurring method may be applied. We apply a median blur when the --preprocess flag is set to blur. 
Applying a median blur can help reduce salt and pepper noise, again making it easier for Tesseract 
to correctly OCR the image.

After pre-processing the image, we use  os.getpid to derive a temporary image filename based on the process ID 
of our Python script.

The final step before using pytesseract for OCR is to write the pre-processed image, gray, 
to disk saving it with the filename  from above
'''

# load the image as a PIL/Pillow image, apply OCR, and then delete the temporary file
text = pytesseract.image_to_string(Image.open(filename), lang = 'eng')
os.remove(filename)

# Cleaning all the gibberish text
text = ftfy.fix_text(text)
text = ftfy.fix_encoding(text)
#print(text)

### DOB extraction
matches=list(datefinder.find_dates(text))

if len(matches) > 0:
    # date returned will be a datetime.datetime object. here we are only using the last match as that will certainly be the DOB
    date = matches[(len(matches)-1)]
    dob=str(date)
    dob=dob.split(' ')
    print("DOB in YYYY-MM-DD format : ",dob[0])
else:
    print('Cannot extract DOB')
flag=0
### Pan number extraction
text1=text.split() # list of all groups of letters recognized (split on any whitespace)
for i in text1:
    if(i.isalpha()): # checking if only alphabets then word cannot be PAN no
    	pass
    elif(i.isnumeric()): # checking if only numbers then word cannot be PAN no
    	pass
    else:
    	if(i.isalnum()): # checking if has only letters & numeric no symbols
    		print("PAN Number is : ",i)
    		flag=1
    		break
if(flag==0):
    print('Cannot extract PAN number')
print('Thank you !')
