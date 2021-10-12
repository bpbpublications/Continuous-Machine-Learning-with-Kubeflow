import streamlit as st
import cv2
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt
import io
import cv2 as cv
import os
import glob
import requests
from bs4 import BeautifulSoup
import urllib.request
import random
import pandas as pd
from io import BytesIO
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

def main():
        st.markdown("![Alt Text](https://raw.githubusercontent.com/aniruddhachoudhury/AR-RL-/master/CoMPUTER%20VISION.gif)")
        st.title("Computer Vision  Use Case")
        st.sidebar.subheader("Choose Computer Vision Model")
        model = st.sidebar.selectbox("Model", ("Pencil Sketch","Crop Image","Sharp Image","Color Spacer","Comic Reader"))

        def dodgeV2(x, y):
            return cv2.divide(x, 255 - y, scale=256)

        def pencilsketch(inp_img):
            img_gray = cv2.cvtColor(inp_img, cv2.COLOR_BGR2GRAY)
            img_invert = cv2.bitwise_not(img_gray)
            img_smoothing = cv2.GaussianBlur(img_invert, (21, 21),sigmaX=0, sigmaY=0)
            final_img = dodgeV2(img_gray, img_smoothing)
            return(final_img)
        
        st.write("This Web App is to help convert your photos to realistic  images")
        st.set_option('deprecation.showfileUploaderEncoding', False)

        file_image = st.sidebar.file_uploader("Upload your Photos", type=['jpeg','jpg','png'])
        print(file_image)
        st.set_option('deprecation.showfileUploaderEncoding', False)

        if model == "Pencil Sketch":
                st.subheader("PencilSketcher app to Cartoon Image")
                if file_image is None:
                    st.write("You haven't uploaded any image file")
                     #text_io = io.TextIOWrapper(file_image)
                     #if text_io is None:
                        
                else:
                        input_img = Image.open(file_image)
                        final_sketch = pencilsketch(np.array(input_img))
                        st.write("**Input Photo**")
                        st.image(input_img, use_column_width=True)
                        st.write("**Output Pencil Sketch**")
                        st.image(final_sketch, use_column_width=True)

        if model == "Crop Image":
                st.subheader("Crop your Image app to your size")
                if file_image is None:
                   # text_io = io.TextIOWrapper(file_image)
                    #if text_io is None:
                        st.write("You haven't uploaded any image file")

                else:
                        input_img = Image.open(file_image)
                        image = np.array(input_img)
                        x, y = image.shape[:2]
                        height, width = image.shape[:2]
                        print(height,width)
                        st.sidebar.subheader("Choose Pixel for image")
                        # Let's get the starting pixel coordiantes (top  left of cropping rectangle)
                        startrowper=st.sidebar.slider("Start Row", min_value=0., max_value=1.0)
                        startcolper=st.sidebar.slider("Start Column", min_value=0., max_value=1.0 )
                        endrowper=st.sidebar.slider("End Row", min_value=0., max_value=1.0 )
                        endcolper=st.sidebar.slider("End Column", min_value=0., max_value=1.0)
                        Crop = st.sidebar.selectbox("You want to Crop", ("Yes", "No"))
                        if Crop=='Yes':
                            start_row, start_col = int(height * startrowper), int(width * startcolper)

                            # Let's get the ending pixel coordinates (bottom right)
                            end_row, end_col = int(height * endrowper), int(width * endcolper)

                            # Simply use indexing to crop out the rectangle we desire
                            cropped = image[start_row:end_row , start_col:end_col]

                            row, col = 1, 2
                            fig, axs = plt.subplots(row, col, figsize=(15, 10))
                            fig.tight_layout()
                            
                            axs[0].imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                            axs[0].set_title('Original Image')
                            cv2.imwrite('original_image.png', image)
                            st.image('original_image.png', use_column_width=True)

                            axs[1].imshow(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))
                            axs[1].set_title('Cropped Image')
                            cv2.imwrite('cropped_image.png', cropped)

                            st.image('cropped_image.png', use_column_width=True)
                        else:
                            st.write("You don't want to crop")

        if model == "Sharp Image":
                st.subheader("Sharpen your Image")
                if st.sidebar.button('Changer'):
                    showpred = 1
                    if file_image is None:
                        #text_io = io.TextIOWrapper(file_image)
                       # if text_io is None:
                        st.write("You haven't uploaded any image file")

                    else:
                            input_img = Image.open(file_image)
                            image = np.array(input_img)
                            row, col = 1, 2
                            fig, axs = plt.subplots(row, col, figsize=(15, 10))
                            #fig.tight_layout()

                            axs[0].imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                            axs[0].set_title('Original Image')

                            # Create our shapening kernel, we don't normalize since the 
                            # the values in the matrix sum to 1
                            kernel_sharpening = np.array([[-1,-1,-1], 
                                                        [-1,9,-1], 
                                                        [-1,-1,-1]])

                            # applying different kernels to the input image
                            sharpened = cv2.filter2D(image, -1, kernel_sharpening)

                            axs[1].imshow(cv2.cvtColor(sharpened, cv2.COLOR_BGR2RGB))
                            axs[1].set_title('Image Sharpening')
                            st.image(input_img, use_column_width=True)
                            cv2.imwrite('sharpen_image.jpg', sharpened)

                            st.image('sharpen_image.jpg', use_column_width=True)
            
        if model == "Color Spacer":
                st.subheader("Sharpen your Image") 
                cs = ["bw","hsv","yuv","lab"]
                color_space = st.sidebar.selectbox("Pick a space.", cs)
                if st.sidebar.button('Changer'):
                    showpred = 1
                    if file_image is None:
                        #text_io = io.TextIOWrapper(file_image)
                       # if text_io is None:
                            st.write("You haven't uploaded any image file")

                    else:
                            input_img = Image.open(file_image)
                            st.write("**Input Photo**")
                            st.image(input_img, use_column_width=True)
                            src = np.array(input_img)
                            if color_space == "bw":
                                    image = cv.cvtColor(src, cv.COLOR_BGR2GRAY ) 
                            if color_space == "hsv":
                                    image = cv.cvtColor(src, cv.COLOR_BGR2HSV )     
                            if color_space == "yuv":
                                    image = cv.cvtColor(src, cv.COLOR_BGR2YUV )
                            if color_space == "lab":
                                    image = cv.cvtColor(src, cv.COLOR_BGR2LAB )        
                            st.write("**Output Pencil Sketch**")
                            st.image(image,use_column_width=True)

        if model == "Comic Reader":
                st.subheader("Comic Reader time ")                     
                cs = ["xkcd","Calvin and Hobbes"]
                st.sidebar.title("The Free Comic Foundation")
                #selected_image = st.sidebar.selectbox("Pick an image.", images)
                color_space = st.sidebar.selectbox("Pick a comic.", cs)


                st.write("Your favorite comic")
                ind = 1
                if st.sidebar.button('Load Comic'):
                    if color_space == "Calvin and Hobbes":
                        url = "https://www.gocomics.com/comics/lists/1643242/calvin-and-hobbes-bedtime?page="+str(random.randint(1, 20))                          
                        response = requests.get(url)
                        soup = BeautifulSoup(response.text, "html.parser")
                        images = soup.findAll('img')
                        url = images[(random.randint(1, 5))]['src']
                        urllib.request.urlretrieve(url, r"r.jpg")
                        image = Image.open(r"r.jpg")
                        st.image(image)
                    if color_space == "xkcd":
                        url = "https://xkcd.com/"+str(random.randint(1, 1000))+"/"
                        response = requests.get(url)
                        soup = BeautifulSoup(response.text, "html.parser")
                        images = soup.findAll('img')
                        i = 0
                        for image in images:
                            i = i+1
                            if i==3:
                                gg = image['src']
                                #print(image['src'])
                        urllib.request.urlretrieve("https:"+gg, r"r.jpg")
                        image = Image.open(r"r.jpg")
                        st.image(image)

              

if __name__ == '__main__':
    main()
     