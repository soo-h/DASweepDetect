import sys
import numpy as np
from sklearn.model_selection import train_test_split
from util.check_tools import get_input_file
import os


## 输入配置文件
ipt = sys.argv[1]
config = sys.argv[2]
outdir = sys.argv[3]



featureMapSet = get_input_file(ipt)



with open(config,'r') as f:
    lab_dict = {}
    for line in f:
        if line:
            name,label = line.strip().split()
            lab_dict[name] = int(label)

if len(featureMapSet) != len(lab_dict.keys()):
    print("Error: Feature map and label do not match!!!")
    sys.exit()

def label_gene(clsName,lab_dict):
    """
    后期具体化name,通过查询字典直接返回label
    """    
    query = False
    
    for name in lab_dict:
        if name in clsName:
            return lab_dict[name]
        
    if not query:
        sys.exit('ClassName Error: Name not in dict !!!')
    return 0

if len(lab_dict.keys()) != len(featureMapSet):
    sys.exit("Error: Number of sample classify not compare with Number of label !!!")

dataSet = []
dataLabel = []
for featureMap_name in featureMapSet:
    featureMap = np.load(featureMap_name)
    sample_number = featureMap.shape[0]
    label = label_gene(featureMap_name,lab_dict)
    dataLabel.append(np.repeat(label,sample_number))
    dataSet.append(featureMap)

dataSet = np.concatenate(dataSet)
dataSet[np.isnan(dataSet)] = 0

dataLabel = np.concatenate(dataLabel)


## 划分训练集、验证集、测试集
dataSet_train,dataSet_val,label_train,label_val = train_test_split(dataSet,dataLabel,test_size=0.2)
dataSet_val,dataSet_test,label_val,label_test = train_test_split(dataSet_val,label_val,test_size=0.5)

np.save(f'{outdir}trainSet',dataSet_train)
np.save(f'{outdir}trainSet_label',label_train)

np.save(f'{outdir}validSet',dataSet_val)
np.save(f'{outdir}validSet_label',label_val)

np.save(f'{outdir}testSet',dataSet_test)
np.save(f'{outdir}testSet_label',label_test)
