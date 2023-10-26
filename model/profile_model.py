from mnist import save_model, instantiate_model, load_model
from path import tf_model_path, tf_ft_model_path, coreml_model_path
import tensorflow as tf
import numpy as np 
import sys
from memory_profiler import profile
import cProfile
import multiprocessing as mp
import psutil
import time

def monitor(target):
    worker_process = mp.Process(target=target)
    worker_process.start()
    p = psutil.Process(worker_process.pid)

    # log cpu usage of `worker_process` every 10 ms
    cpu_percents = []
    while worker_process.is_alive():
        cpu_percents.append(p.cpu_percent())
        time.sleep(0.0001)

    worker_process.join()
    return cpu_percents

def keras_main():
    model = tf.keras.models.load_model(tf_ft_model_path())
    model.predict(np.zeros((2, 28, 28, 1)), verbose=0)

def coreml_main():
    import coremltools as ct
    core_model = ct.models.MLModel(str(coreml_model_path()))
    core_model.predict({"input": np.zeros((2, 28, 28, 1))})

if __name__ == "__main__":
    if sys.argv[-1] == "keras": 
        # cProfile.run('keras_main()')
        monitor(target=keras_main)
    else:
        # cProfile.run('coreml_main()')
        monitor(target=coreml_main)