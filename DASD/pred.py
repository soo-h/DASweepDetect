import sys
import numpy as np
import tensorflow as tf

def max_minNorm(data):
    if np.ndim(data) == 3:
        max_value = np.max(data,axis=(0,2)).reshape(1,data.shape[1],1)
        min_value = np.min(data,axis=(0,2)).reshape(1,data.shape[1],1)
        denominator = max_value - min_value

    else:
        sys.exit("Need dim is 3, but input dim is %d. \n" % (np.ndim(data)))

    return (data - min_value) / denominator


def get_mid_positions(left,right):
    length = right - left
    mid1 = left + length * 9/20
    mid2 = left + length * 11/20
    return mid1, mid2
def read_pos_info(pos_info):
    region = []
    with open(pos_info) as f:
        for line in f:
            left,right = line.strip().split()
            left,right = float(left),float(right)
            left,right = get_mid_positions(left,right)
            region.append('\t'.join([str(left),str(right)]))
    return region


model_name = sys.argv[1]
feature_map_name = sys.argv[2]
pos_info_name = sys.argv[3]
out_name = sys.argv[4]

pos_info = read_pos_info(pos_info_name)

real_data = np.load(feature_map_name)
real_data = max_minNorm(real_data)


model = tf.keras.models.load_model(model_name)


pred_situ,clas_situ = model(real_data,1.)

## 输出预测结果
assert len(pred_situ) == len(pos_info)

with open(out_name,'w') as f:
    f.write('\t'.join(['pos_left','pos_right','class','prob'])+'\n')
    for i in range(len(pred_situ)):
        pred = pred_situ[i]
        f.write(pos_info[i] + '\t' + str(np.argmax(pred)) + '\t' + str(np.max(pred)) + '\n')