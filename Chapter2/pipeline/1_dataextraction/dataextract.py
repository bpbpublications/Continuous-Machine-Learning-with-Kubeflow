from __future__ import absolute_import, division, print_function, unicode_literals
import click
import json
import os
import numpy as np
import argparse
import dill
import pandas as pd
from sklearn.datasets import load_breast_cancer



@click.command()
@click.option('--data-file', default="/mnt/breast.data")
def get_data(data_file):
  
   cancer = load_breast_cancer()
   df_cancer = pd.DataFrame(np.c_[cancer['data'], cancer['target']], columns = np.append(cancer['feature_names'], ['target']))
   print(df_cancer.head(3))

   print(df_cancer.describe())
   with open(data_file,"wb") as f:
       dill.dump(df_cancer,f)

    
   return


if __name__ == "__main__":
    get_data()