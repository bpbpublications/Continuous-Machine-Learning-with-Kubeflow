from __future__ import absolute_import, division, print_function, unicode_literals
import click
import json
import os
import argparse
from tensorflow.python.lib.io import file_io
import dill
import pandas as pd
from sklearn.model_selection import train_test_split
from google.cloud import storage
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "service_account_iam.json"


def correlation_plotting(data,s,correlation_plot):    
    correlation = data.corr()
    matrix_cols = correlation.columns.tolist()
    corr_array  = np.array(correlation)
    #Plotting

    trace = go.Heatmap(z = corr_array,
                       x = matrix_cols,
                       y = matrix_cols,
                       xgap = 2,
                       ygap = 2,
                       colorscale='Viridis',
                       colorbar   = dict() ,
                      )
    layout = go.Layout(dict(title = 'Correlation Matrix' +s,
                            autosize = False,
                            height  = 720,
                            width   = 800,
                            margin  = dict(r = 0 ,l = 210,
                                           t = 25,b = 210,
                                         ),
                            yaxis   = dict(tickfont = dict(size = 9)),
                            xaxis   = dict(tickfont = dict(size = 9)),
                           )
                      )
    fig = go.Figure(data = [trace],layout = layout)
    fig.update_layout( 
                    title={
                        'y':1,
                        'x':0.6,
                        'xanchor': 'center',
                        'yanchor': 'top'})
    
    fig.write_image(correlation_plot)



@click.command()
@click.option('--data-file', default="/mnt/breast.data")
@click.option('--train-file', default="/mnt/training.data")
@click.option('--test-file', default="/mnt/test.data")
@click.option('--validation-file', default="/mnt/validation.data")
@click.option('--train-target', default="/mnt/trainingtarget.data")
@click.option('--test-target', default="/mnt/testtarget.data")
@click.option('--validation-target', default="/mnt/validationtarget.data")
@click.option('--split-size', default=0.1)
@click.option('--bucket-data', default="gs://kubeflowusecases/breast/data.csv")
@click.option('--bucket-name', default="gs://kubeflowusecases")
@click.option('--commit-sha', default="breast/visualize")
@click.option('--metrics-plot', default="/mnt/correlation.png")
def training_data_processing(data_file,train_file,test_file,metrics_plot,validation_file,split_size,train_target,test_target,validation_target,bucket_data,bucket_name,commit_sha):

    with open(data_file, 'rb') as in_f:
        data= dill.load(in_f)
        
    data=data.fillna(data.mean())
    
    correlation_plotting(data,"for the Breast Cancer Dataset",metrics_plot)

    image_path = os.path.join(bucket_name, commit_sha, 'correlation.png')
    image_url = os.path.join('https://storage.cloud.google.com', bucket_name.lstrip('gs://'), commit_sha, 'correlation.png?authuser=0')
    html_path = os.path.join(bucket_name, commit_sha,'correlation.html')

    data.to_csv(bucket_data) 
    header = data.columns.tolist()

    file_io.copy(metrics_plot, image_path)
    rendered_template = """
        <html>
            <head>
                <title>Correlation</title>
            </head>
            <body>
                <img src={}>
            </body>
        </html>""".format(image_url)
    file_io.write_string_to_file(html_path, rendered_template)




    metadata = {
        'outputs' : [{
            'type': 'table',
            'storage': 'gcs',
            'format': 'csv',
            'header': header,
            'source': bucket_data
            },{
        'type': 'web-app',
        'storage': 'gcs',
        'source': html_path,
        }]
        }

    with open('/mlpipeline-ui-metadata.json', 'w') as f:
        json.dump(metadata, f)

    target_name = 'target'
    data_target = data[target_name]
    data = data.drop([target_name], axis=1)
   
     #%% split training set to validation set
    train, test, target, target_test = train_test_split(data, data_target, test_size=split_size, random_state=0)
    Xtrain, Xval, Ztrain, Zval = train_test_split(train, target, test_size=split_size, random_state=0)

    
    
    print(len(Xtrain), 'train examples')
    print(len(test), 'validation examples')
    print(len(Xval), 'test examples')
    


    


    with open(train_file,"wb") as f:
        dill.dump(Xtrain,f) 
    
    with open(test_file,"wb") as f:
        dill.dump(test,f) 
        
    with open(validation_file,"wb") as f:
        dill.dump(Xval,f) 
    
    with open(train_target,"wb") as f:
        dill.dump(Ztrain,f) 
    
    with open(test_target,"wb") as f:
        dill.dump(target_test,f) 
        
    with open(validation_target,"wb") as f:
        dill.dump(Zval,f) 
    return


if __name__ == "__main__":
    training_data_processing()