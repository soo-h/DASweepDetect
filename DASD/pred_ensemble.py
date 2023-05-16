import sys
import os

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


model_path = sys.argv[1]
M = int(sys.argv[2])
feature_map_name = sys.argv[3]
pos_info_name = sys.argv[4]
out_name = sys.argv[5]

if not model_path.endswith('/'):
    model_path += '/'

sub_model_path = [f'{model_path}{dir}' for dir in  os.listdir(model_path) if os.path.isdir(f"{model_path}{dir}")]
print(sub_model_path)

if len(sub_model_path) != M:
    raise ValueError("The number of models identified does not match the number of models given!!")


pos_info = read_pos_info(pos_info_name)
real_data = np.load(feature_map_name)
real_data = max_minNorm(real_data)

# Ensemble
clss = M
pred_Ensemble = np.zeros((real_data.shape[0], clss))

for m in range(len(sub_model_path)):
    dirpath = sub_model_path[m]
    model = tf.keras.models.load_model(dirpath)

    pred,_= model(real_data, 1.)
    pred_Ensemble += pred

pred_Ensemble = pred_Ensemble / M


# 输出预测结果
if len(pred_Ensemble) != len(pos_info):
    raise ValueError("The location information does not match the predicted result.\
    \nCheck whether the input file is correct!!!")

with open(out_name,'w') as f:
    f.write('\t'.join(['pos_left','pos_right','class','prob',"all_prob"])+'\n')
    for i in range(len(pred_Ensemble)):
        pred = np.asarray(pred_Ensemble[i])
        f.write(pos_info[i] + '\t' + str(np.argmax(pred)) + '\t' + str(np.max(pred)) \
                 + '\t' + ','.join([str(x) for x in pred]) + '\n')
