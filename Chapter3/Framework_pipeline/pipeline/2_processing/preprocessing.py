from __future__ import absolute_import, division, print_function, unicode_literals
import click
import json
import os
import argparse
import dill
from tqdm import tqdm
import cv2
import numpy as np
import imutils
import tensorflow as tf




def load_data_array(dir_path, img_size=(100,100)):
    """
    Load resized images as np.arrays to workspace
    """
    X = []
    y = []
    i = 0
    labels = dict()
    for path in tqdm(sorted(os.listdir(dir_path))):
        if not path.startswith('.'):
            labels[i] = path
            for file in os.listdir(dir_path + path):
                if not file.startswith('.'):
                    img = cv2.imread(dir_path + path + '/' + file)
                    X.append(img)
                    y.append(i)
            i += 1
    X = np.array(X)
    y = np.array(y)
    print(f'{len(X)} images loaded from {dir_path} directory.')
    return X, y, labels

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


def save_new_images(x_set, y_set, folder_name):
    i = 0
    for (img, imclass) in zip(x_set, y_set):
        if imclass == 0:
            cv2.imwrite(folder_name+'NO/'+str(i)+'.jpg', img)
        else:
            cv2.imwrite(folder_name+'YES/'+str(i)+'.jpg', img)
        i += 1

def preprocess_images(set_name, img_size):
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

@click.command()
@click.option('--root',default="/mnt/")
@click.option('--train-file', default="/mnt/training.data")
@click.option('--test-file', default="/mnt/test.data")
@click.option('--validation-file', default="/mnt/validation.data")
@click.option('--train-target', default="/mnt/trainingtarget.data")
@click.option('--test-target', default="/mnt/testtarget.data")
@click.option('--validation-target', default="/mnt/validationtarget.data")
@click.option('--label', default="/mnt/labels.data")
@click.option('--image-size', default=224)
def training_data_processing(root,train_file,label,test_file,validation_file,image_size,train_target,test_target,validation_target):


    TRAIN_DIR = root + 'TRAIN/'
    TEST_DIR = root + 'TEST/'
    VAL_DIR = root + 'VAL/'
    IMG_SIZE = (image_size,image_size)

    # use predefined function to load the image data into workspace
    X_train, y_train, labels = load_data_array(TRAIN_DIR, IMG_SIZE)
    X_test, y_test, _ = load_data_array(TEST_DIR, IMG_SIZE)
    X_val, y_val, _ = load_data_array(VAL_DIR, IMG_SIZE)
    
    # apply this for each set
    X_train_crop = crop_imgs(set_name=X_train)
    X_val_crop = crop_imgs(set_name=X_val)
    X_test_crop = crop_imgs(set_name=X_test)



    directory=["TRAIN_CROP" ,"TEST_CROP" ,"VAL_CROP" ,"TRAIN_CROP/YES" ,"TRAIN_CROP/NO" ,"TEST_CROP/YES" , "TEST_CROP/NO" ,"VAL_CROP/YES" ,"VAL_CROP/NO"]
    for i in directory:
        path = os.path.join(root, i)
        try:  
            os.mkdir(path)  
        except OSError as error:  
            print(error)

    save_new_images(X_train_crop, y_train, folder_name='/mnt/TRAIN_CROP/')
    save_new_images(X_val_crop, y_val, folder_name='/mnt/VAL_CROP/')
    save_new_images(X_test_crop, y_test, folder_name='/mnt/TEST_CROP/')


   
    X_train_prep = preprocess_images(set_name=X_train_crop, img_size=IMG_SIZE)
    X_test_prep = preprocess_images(set_name=X_test_crop, img_size=IMG_SIZE)
    X_val_prep = preprocess_images(set_name=X_val_crop, img_size=IMG_SIZE)




    print(len(X_train_prep), 'train examples for prep')
    print(len(X_val_prep), 'validation examples for prep')
    print(len(X_test_prep), 'test examples for prep')
   
   
   
    with open(label,"wb") as f:
        dill.dump(labels,f) 

    with open(train_file,"wb") as f:
        dill.dump(X_train_prep,f) 
    
    with open(test_file,"wb") as f:
        dill.dump(X_test_prep,f) 
        
    with open(validation_file,"wb") as f:
        dill.dump(X_val_prep,f) 
    
    with open(train_target,"wb") as f:
        dill.dump(y_train,f) 
    
    with open(test_target,"wb") as f:
        dill.dump(y_test,f) 
        
    with open(validation_target,"wb") as f:
        dill.dump(y_val,f) 
    return


if __name__ == "__main__":
    training_data_processing()