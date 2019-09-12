'''
here a fake time consuming task for dev
'''
import os
import inspect
import time
import random

from analyze import predict
from keras.models import Model, load_model
from keras import backend as K

ALLOWED_EXTENSION = ('.tif', '.jpg', '.jpeg')  # lower, jpg/.jpeg for test purpose


def time_consuming_task(fp, task_id, callback):
    if not isinstance(fp, str):
        raise TypeError

    if not os.path.exists(fp):
        raise FileNotFoundError

    if not os.path.isdir(fp):
        raise ValueError

    if not isinstance(task_id, int):
        raise TypeError

    if task_id < 1:
        raise ValueError

    if not inspect.isfunction(callback):
        raise TypeError

    # add process here
    #create folders
    if(os.path.exists((fp+'/coordinates'))):
      pass
    else:
      os.mkdir((fp+'/coordinates'))

    if(os.path.exists((fp+'/labels'))):
      pass
    else:
      os.mkdir((fp+'/labels'))
    print("Loading in trained model...")
    model = load_model('ecDNA_model.h5') #load model
    for f in os.listdir(fp): #get all images in path
        ext = os.path.splitext(f)[1]
        if ext.lower() == '.tif':
          print('Segmenting',f)
          predict.predict(model, fp, (f))
    print("Successfully exited...")
    K.clear_session()
    
    callback(task_id, 2)
    # 2 -- success
    # 3 -- failed
