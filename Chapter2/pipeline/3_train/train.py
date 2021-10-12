from __future__ import absolute_import, division, print_function, unicode_literals
import click
import dill
import json
import logging
import os
import pandas as pd
import tensorflow as tf
from storage import Storage

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "service_account_iam.json"


def model_build(Xtrain):
    model = tf.keras.models.Sequential([
    tf.keras.layers.Dense(units=32, kernel_initializer='glorot_uniform',activation='relu', input_shape=(len(Xtrain.columns),)),
    tf.keras.layers.Dense(units=64, kernel_initializer='glorot_uniform',activation='relu'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(units=64, kernel_initializer='glorot_uniform',activation='relu'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(units=1, kernel_initializer='glorot_uniform', activation='sigmoid')
    ])
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
@click.option('--batch-size', default=4)
@click.option('--learning-rate', default=0.001)
@click.option('--tensorboard-logs', default='/mnt/logs/')
@click.option('--tensorboard-gcs-logs', default='gs://kubeflowusecases/breast/logs')
@click.option('--model-output-base-path', default="/mnt/saved_model")
@click.option('--gcs-path', default="gs://kubeflowusecases/breast/model")
@click.option('--mode', default="local")
def train_model(train_file,test_file,validation_file,train_target,test_target,validation_target,epochs,batch_size,learning_rate,tensorboard_logs,tensorboard_gcs_logs,model_output_base_path,gcs_path,mode):
        
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


        strategy = tf.distribute.experimental.MultiWorkerMirroredStrategy()
        logging.info("Number of devices: {0}".format(strategy.num_replicas_in_sync))
        with strategy.scope():

                optimizer = tf.keras.optimizers.Adam(learning_rate)
                model = model_build(train)
                model.compile(optimizer=optimizer, loss=tf.keras.losses.binary_crossentropy,metrics=['accuracy'])
                
                TF_STEPS_PER_EPOCHS=5
                BATCH_SIZE = batch_size * strategy.num_replicas_in_sync
                tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=tensorboard_logs, histogram_freq=1)
                logging.info("Training starting...")
                model.fit(train,train_tar, epochs=epochs, batch_size=BATCH_SIZE,
                     validation_data=(validation, validation_tar),callbacks=[tensorboard_callback])
                logging.info("Training completed.")
                model.save(model_output_base_path) 

        new_model = tf.keras.models.load_model(model_output_base_path)
        # Check its architecture
        print(new_model.summary())
    

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