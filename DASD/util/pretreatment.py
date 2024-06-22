import numpy as np
import sys

def dim_check(data):
    if np.ndim(data) != 3:
        sys.exit("Need dim is 3, but input dim is %d. \n" % (np.ndim(data)))
    return 0

def max_minNorm(data):
    data[np.isnan(data)] = 0
    dim_check(data)
    # max-min normalization
    max_value = np.max(data,axis=(0,2)).reshape(1,data.shape[1],1)
    min_value = np.min(data,axis=(0,2)).reshape(1,data.shape[1],1)
    denominator = max_value - min_value


    return (data - min_value) / denominator