import os
import tensorflow as tf 
import sys
import json    
import numpy as np 
import kfserving
from typing import List, Dict



class KFServingSampleModel(kfserving.KFModel):
    def __init__(self, name: str):
        super().__init__(name)
        self.name = name
        self.ready = False
        self.model_output_base_path = "gs://kubeflowusecases/breast/model/"

    def load(self):
        model = tf.keras.models.load_model(self.model_output_base_path)
        self.model = model
        self.ready = True

    def predict(self, request: Dict) -> Dict:
        inputs = np.array(request["instances"])
        reshaped_to_2d = np.reshape(inputs, (-1, len(inputs)))
        results = self.model.predict(reshaped_to_2d)
        result = (results > 0.5)*1 
        if result==1:
            result="malignant"
        else:
            result="Benign"
        
        print("result : {0}".format(result))
        return {"predictions": result}


if __name__ == "__main__":
    model = KFServingSampleModel("kfserving-breast-model")
    model.load()
    kfserving.KFServer(workers=1).start([model])
        
