from __future__ import absolute_import, division, print_function, unicode_literals
import click
import dill
import json
import logging
import os
import pandas as pd
import tensorflow as tf
from storage import Storage
from sklearn.metrics import accuracy_score
import PIL




def model_build(base_model,NUM_CLASSES,activation):
    model = tf.keras.models.Sequential([
        base_model,
         tf.keras.layers.Flatten(),
         tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(NUM_CLASSES,activation=activation),
    ])
    model.layers[0].trainable = False
    return model




def get_callbacks(path):
    checkpointdir = path
    class customLog(tf.keras.callbacks.Callback):
        def on_epoch_end(self, epoch, logs={}):
            logging.info('epoch: {}'.format(epoch + 1))
            logging.info('loss={}'.format(logs['loss']))
            logging.info('accuracy={}'.format(logs['accuracy']))
            logging.info('val_loss={}'.format(logs['val_loss']))
            logging.info('val_accuracy={}'.format(logs['val_accuracy']))
    callbacks = [tf.keras.callbacks.ModelCheckpoint(filepath=checkpointdir),customLog()]
    return callbacks



@click.command()
@click.option('--train-file', default="/mnt/training.data")
@click.option('--test-file', default="/mnt/test.data")
@click.option('--validation-file', default="/mnt/validation.data")
@click.option('--train-target', default="/mnt/trainingtarget.data")
@click.option('--test-target', default="/mnt/testtarget.data")
@click.option('--validation-target', default="/mnt/validationtarget.data")
@click.option('--epochs', default=100)
@click.option('--activation', default="sigmoid")
@click.option('--learning-rate', default=0.001)
@click.option('--tensorboard-logs', default='/mnt/logs/')
@click.option('--tensorboard-gcs-logs', default='gs://kubeflowusecases/brain/logs')
@click.option('--model-output-base-path', default="/mnt/saved_model")
@click.option('--gcs-path', default="gs://kubeflowusecases/brain/model")
@click.option('--mode', default="local")
@click.option('--image-size', default=224)
@click.option('--label', default="/mnt/labels.data")
def train_model(train_file,test_file,validation_file,train_target,test_target,validation_target,
label,epochs,activation,image_size,learning_rate,tensorboard_logs,tensorboard_gcs_logs,model_output_base_path,gcs_path,mode):
        
        with open(label, 'rb') as in_f:
                labels= dill.load(in_f)

        with open(train_file, 'rb') as in_f:
                train= dill.load(in_f)
     
       
        with open(test_file, 'rb') as in_f:
                test= dill.load(in_f)
    

        with open(validation_file, 'rb') as in_f:
                validation= dill.load(in_f)
        
        with open(train_target, 'rb') as in_f:
                train_tar= dill.load(in_f)
  
       
        with open(test_target, 'rb') as in_f:
                test_tar= dill.load(in_f)
     

        with open(validation_target, 'rb') as in_f:
                validation_tar= dill.load(in_f)


        IMG_SIZE = (image_size,image_size)
        RANDOM_SEED = 123
        TRAIN_DIR = '/mnt/TRAIN_CROP/'
        VAL_DIR = '/mnt/VAL_CROP/'
        
        train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(
                rotation_range=15,
                width_shift_range=0.1,
                height_shift_range=0.1,
                shear_range=0.1,
                brightness_range=[0.5, 1.5],
                horizontal_flip=True,
                vertical_flip=True,
                preprocessing_function=tf.keras.applications.vgg16.preprocess_input
                )

        train_generator = train_datagen.flow_from_directory(
                        TRAIN_DIR,
                        color_mode='rgb',
                        target_size=IMG_SIZE,
                        batch_size=32,
                        class_mode='binary',
                        seed=RANDOM_SEED
                )

        val_datagen = tf.keras.preprocessing.image.ImageDataGenerator(
        preprocessing_function=tf.keras.applications.vgg16.preprocess_input)

        validation_generator = val_datagen.flow_from_directory(
                                VAL_DIR,
                                color_mode='rgb',
                                target_size=IMG_SIZE,
                                batch_size=16,
                                class_mode='binary',
                                seed=RANDOM_SEED
                                )


        vgg16_weight_path="/app/vgg16_weights_tf_dim_ordering_tf_kernels_notop.h5"
        base_model=tf.keras.applications.VGG16(
                include_top=False, weights=vgg16_weight_path, input_shape=IMG_SIZE + (3,)
                )


        NUM_CLASSES=1
        model=model_build(base_model,NUM_CLASSES,activation)
        optimizer=tf.keras.optimizers.RMSprop(learning_rate=learning_rate)
        model.compile(
                        loss=tf.keras.losses.binary_crossentropy,
                        optimizer=optimizer,
                        metrics=['accuracy']
                        )
        tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=tensorboard_logs, histogram_freq=1)
        
        earlystopping = tf.keras.callbacks.EarlyStopping(
                        monitor='val_loss', 
                        mode='max',
                        patience=6
                        )
        logging.info("Training starting...")
        model.fit_generator(
                train_generator,
                #steps_per_epoch=50,
                epochs=epochs,
                validation_data=validation_generator,
                validation_steps=25,
                callbacks=[earlystopping,tensorboard_callback])
        logging.info("Training completed.")
        model.save(model_output_base_path)
        new_model = tf.keras.models.load_model(model_output_base_path)
        # Check its architecture
        print(new_model.summary())


        predictions = new_model.predict(validation)
        predictions = [1 if x>0.5 else 0 for x in predictions]

        accuracy = accuracy_score(validation_tar, predictions)
        print('Val Accuracy = %.2f' % accuracy)
        logging.info(('Val Accuracy = %.2f' % accuracy))
        Storage.upload(tensorboard_logs,tensorboard_gcs_logs)
        
        metadata = {
                'outputs': [{
                        'type': 'tensorboard',
                        'source': tensorboard_gcs_logs,
                                
                }]
                }
        with open("/mlpipeline-ui-metadata.json", 'w') as f:
                json.dump(metadata,f)

        if mode!= 'local':
                print("uploading to {0}".format(gcs_path))
                Storage.upload(model_output_base_path,gcs_path)

        else:
                print("Model will not be uploaded")
                pass
    
   
if __name__ == "__main__":
    train_model()
    