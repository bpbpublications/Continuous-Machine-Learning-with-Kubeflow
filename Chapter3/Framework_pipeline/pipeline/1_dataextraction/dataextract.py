from __future__ import absolute_import, division, print_function, unicode_literals
import click
import json
import os
import argparse
import dill
import kaggle
import logging
import shutil
import itertools




@click.command()
@click.option('--data-file', default="/mnt/BrainScan_Data/")
@click.option('--root',default="/mnt/")
@click.option('--kaggle-api-data',default="navoneel/brain-mri-images-for-brain-tumor-detection")
def download_data(root,data_file,kaggle_api_data):

    logging.info(kaggle.api.authenticate())
    kaggle.api.dataset_download_files(kaggle_api_data, path=data_file, unzip=True)
    logging.info("Downloaded Data")
    print(len(os.listdir( data_file +"brain_tumor_dataset/no")))
    print(len(os.listdir(data_file +"brain_tumor_dataset/yes")))


    directory=["TRAIN" ,"TEST" ,"VAL" ,"TRAIN/YES" ,"TRAIN/NO" ,"TEST/YES"   , "TEST/NO" ,"VAL/YES" ,"VAL/NO"]
    for i in directory:
        path = os.path.join(root, i)
        try:  
            os.mkdir(path)  
        except OSError as error:  
            print(error)

   
    
    for CLASS in os.listdir(data_file):
        logging.info(CLASS)
        print(CLASS)
        if not CLASS.startswith('.'):
            IMG_NUM = len(os.listdir(data_file + CLASS))
            logging.info(IMG_NUM)
            print(IMG_NUM)
            for (n, FILE_NAME) in enumerate(os.listdir(data_file + CLASS)):
                img = data_file + CLASS + '/' + FILE_NAME
                if n < 5:
                    try:  
                        shutil.copy(img, '/mnt/TEST/' + CLASS.upper() + '/' + FILE_NAME)
                        
                    except OSError as error:  
                        print(error)
                elif n < 0.8*IMG_NUM:
                    try:
                        shutil.copy(img, '/mnt/TRAIN/'+ CLASS.upper() + '/' + FILE_NAME)
               
                    except OSError as error:
                         print(error)  
                else:
                    try:
                        shutil.copy(img, '/mnt/VAL/'+ CLASS.upper() + '/' + FILE_NAME)
                  
                    except OSError as error:
                         print(error)
                      
    
    return


if __name__ == "__main__":
    download_data()