import kfserving
from typing import List, Dict
import argparse
import numpy as np
import json
import logging
import cv2
import os
import base64
from PIL import Image
import io
import imutils
import tensorflow as tf






def crop_imgs(set_name, add_pixels_value=0):
    """
    Finds the extreme points on the image and crops the rectangular out of them
    """
    set_new = []
    for img in set_name:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        # threshold the image, then perform a series of erosions +
        # dilations to remove any small regions of noise
        thresh = cv2.threshold(gray, 45, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.erode(thresh, None, iterations=2)
        thresh = cv2.dilate(thresh, None, iterations=2)

        # find contours in thresholded image, then grab the largest one
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        c = max(cnts, key=cv2.contourArea)

        # find the extreme points
        extLeft = tuple(c[c[:, :, 0].argmin()][0])
        extRight = tuple(c[c[:, :, 0].argmax()][0])
        extTop = tuple(c[c[:, :, 1].argmin()][0])
        extBot = tuple(c[c[:, :, 1].argmax()][0])

        ADD_PIXELS = add_pixels_value
        new_img = img[extTop[1]-ADD_PIXELS:extBot[1]+ADD_PIXELS, extLeft[0]-ADD_PIXELS:extRight[0]+ADD_PIXELS].copy()
        set_new.append(new_img)

    return np.array(set_new)

def preprocess_imgs(set_name, img_size):
    """
    Resize and apply VGG-15 preprocessing
    """
    set_new = []
    for img in set_name:
        img = cv2.resize(
            img,
            dsize=img_size,
            interpolation=cv2.INTER_CUBIC
        )
        set_new.append(tf.keras.applications.vgg16.preprocess_input(img))
    return np.array(set_new)


def image_transform(instance):
    # perform pre-processing
    # decode image
    logging.info("Inside Image Transform")
    originalimage = base64.b64decode(instance)
    jpg_as_np = np.frombuffer(originalimage, dtype=np.uint8)
    img = cv2.imdecode(jpg_as_np, flags=1)
    image_expanded = np.expand_dims(img, axis=0)
    crop_image = crop_imgs(set_name=image_expanded)
    IMG_SIZE=(224,224)
    prep_image = preprocess_imgs(set_name=crop_image, img_size=IMG_SIZE)
    return prep_image

class Transformer(kfserving.KFModel):
    def __init__(self, name: str):
        super().__init__(name)
        self.name = name
        self.ready = False
        self.model_output_base_path='gs://kubeflowusecases/brain/model/'


    def load(self):
        self.model = tf.keras.models.load_model(self.model_output_base_path)
        self.ready = True
       
       
    def predict(self, request: Dict) -> Dict:
        
        
        logging.info(type(request))
        #logging.info(request)
        #logging.info(range(len(request['instances'])))
        data={'instances': [image_transform(request['instances'][i]) for i in  range(len(request['instances']))]}        
        #data={'instances': [image_transform(request['instances'][i]) for i in  range(len(request['instances']))]}        
        
        transformdata=[]
        for i in data['instances']:
            logging.info("Inside transform data")
            arraydata=self.model.predict(i)
            logging.info(self.model.predict(i))
            transformdata.append(arraydata)
        
        result=[]
        Predict=0   
        predictions = [1 if x>0.5 else 0 for x in transformdata]    
        for i in predictions:
            if i == Predict:
                    result.append("No tumor inside Brain")
            else:
                    result.append("Tumor inside Brain")
        
        return json.dumps({"predictions" :  result})

if __name__ == "__main__":
    model = Transformer("kfserving-braintumor")
    model.load()
    kfserving.KFServer(workers=1).start([model])

    
