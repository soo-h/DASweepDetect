import numpy as np
import sys

def max_minNorm(data):
    if np.ndim(data) == 3:
        max_value = np.max(data,axis=(0,2)).reshape(1,data.shape[1],1)
        min_value = np.min(data,axis=(0,2)).reshape(1,data.shape[1],1)
        denominator = max_value - min_value

    else:
        sys.exit("Need dim is 3, but input dim is %d. \n" % (np.ndim(data)))

    return (data - min_value) / denominator