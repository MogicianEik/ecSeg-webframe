'''
here a fake time consuming task for dev
'''
import os
import inspect
import time
import random

ALLOWED_EXTENSION = ('.tif', '.jpg', '.jpeg')  # lower, jpg/.jpeg for test purpose


def time_consuming_task(fp, task_id, callback):
    if not isinstance(fp, str):
        raise TypeError

    #if not os.path.exists(fp):
    #    raise FileNotFoundError

    # if not os.path.isdir(fp):
    #    raise ValueError

    if not isinstance(task_id, int):
        raise TypeError

    if task_id < 1:
        raise ValueError

    if not inspect.isfunction(callback):
        raise TypeError
    import os
    os.chdir('/home/eik/Desktop/process/analyze/') # this line needs to be changed according to different local machine, change to the current ecSeg working directory
    os.system('/home/eik/miniconda2/envs/tensorflowproject/bin/python3 ecSeg.py -i "{}"'.format(fp))# this line needs to be changed according to different local machine, replace with the actual path of python3 
    index = 0
    if index == 0:
        callback(task_id, 2)
    else:
        callback(task_id, 3)
    # 2 -- success
    # 3 -- failed
