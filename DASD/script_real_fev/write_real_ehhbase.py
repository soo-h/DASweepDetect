import numpy as np
import sys
sys.path.append('..')
from util import window_tools

## 单倍型方法 的两个思路
## 1. 如下： 
##         <1>单独计算每个dafBin的均值和方差
##         <2>遍历每个大窗口,对每个大窗口利用<1>中的信息，基于相同的dafBin进行标准化

## 2.在1.<1>的同时，直接对所有数据进行标准化，再基于pos和value的对应关系，通过对pos排序完成value的排序



def normBin(filtpos,staValue,freD):
    #filtpos并不需要，但为了使用daf_Win函数，添加filtpos使接口匹配
    freD_dropna = freD[~np.isnan(staValue)]
    filtpos_dropna = np.asarray(filtpos)[~np.isnan(staValue)]
    staValue_dropna = staValue[~np.isnan(staValue)]
    dafBin,ihsBin,posBin = window_tools.daf_Win(freD_dropna,staValue_dropna,filtpos_dropna,region=200)
    ihsBin = [(np.mean(Bin),np.std(Bin)) for Bin in ihsBin]
    return ihsBin

def norm_by_daf(ihsBin,normBin):
    ####normBin和ihsBin长度需相同
    for idx in range(len(ihsBin)):
        if len(ihsBin[idx]):
            if not np.sum(np.isnan(normBin[idx])):
                ihsBin[idx] = (ihsBin[idx] - normBin[idx][0]) / normBin[idx][1]
            else:
                sys.exit('region and entirety not compaer!!!')
    ihsBin = np.abs(np.concatenate(ihsBin))
    return ihsBin

def statCompute(subStatValue,subpos,subfreD,normBin,region=200):
    #传入要进行标准化的统计量
    # 保留位置信息
    locs = window_tools.vector_loc(subpos,region)
    # 去NA
    subfreD = subfreD[~np.isnan(subStatValue)]
    subpos = subpos[~np.isnan(subStatValue)]
    subStatValue = subStatValue[~np.isnan(subStatValue)]
    if len(subpos) > 0:
        # 生成n个bin,分别进行标准化
        dafBin,ihsBin,posBin = window_tools.daf_Win(subfreD,subStatValue,subpos,region)
        ihsNormalize = norm_by_daf(ihsBin,normBin)
        posNormalize = np.concatenate(posBin)
    

        posNormalize,ihsNormalize = window_tools.Phy_Win_real(posNormalize,ihsNormalize,locs)
    else:
        posNormalize,ihsNormalize = np.array([-1]),np.array([-1])

    return posNormalize,ihsNormalize




import copy

#############################方案2###############
def normalize(data):
    mu = np.mean(data)
    sigma = np.std(data)
    return (data - mu) /sigma



def normBin2(filtpos,staVal,freD):
    """
    直接进行标准化
    """
    #filtpos并不需要，但为了使用daf_Win函数，添加filtpos使接口匹配
    staValue = copy.deepcopy(staVal)
    freD_dropna = freD[~np.isnan(staValue)]
    filtpos_dropna = np.asarray(filtpos)[~np.isnan(staValue)]
    staValue_dropna = staValue[~np.isnan(staValue)]
    dafBin,ihsBin,posBin = window_tools.daf_Win(freD_dropna,staValue_dropna,filtpos_dropna,region=200)
    
    posBin = np.concatenate(posBin)
    ihsNormBin = np.concatenate([normalize(Bin) for Bin in ihsBin])
    ihsNormBin_sort = ihsNormBin[np.argsort(posBin)]
    staValue[~np.isnan(staValue)] = ihsNormBin_sort
    
    return staValue


###################################################################


def write_ihs(ihsSet,posSet,dafSet,normBin,fi):
    #奇数行为pos，偶数行为value
    ihsGroupSet = np.zeros(shape=(len(ihsSet),200))
    left = 0

    for idx in range(len(ihsSet)):
        right = left + 1
        subIhsValue = np.asarray(ihsSet[idx],dtype=float)
        subpos = np.asarray(posSet[idx],dtype=float)
        subfreD = np.asarray(dafSet[idx],dtype=float)

        posNormalize,ihsNormalize = statCompute(subIhsValue,subpos,subfreD,normBin,region=200)

        
        ihsGroupSet[left:right] = ihsNormalize
        left = right
    np.savetxt(f'{str(fi)}_ihsStastic', ihsGroupSet)
    
    return 0


def write_dihh(dihhSet,posSet,dafSet,normBin,fi):
    #奇数行为pos，偶数行为value
    dihhGroupSet = np.zeros(shape=(len(dihhSet),200))
    left = 0

    for idx in range(len(dihhSet)):

        right = left + 1

        subIhsValue = np.asarray(dihhSet[idx],dtype=float)
        subpos = np.asarray(posSet[idx],dtype=float)
        subfreD = np.asarray(dafSet[idx],dtype=float)

        posNormalize,dihhNormalize = statCompute(subIhsValue,subpos,subfreD,normBin,region=200)

        dihhGroupSet[left:right] = dihhNormalize
        left = right
    np.savetxt(f'{str(fi)}_dihhStastic', dihhGroupSet)
    return 0


def write_nsl(nslSet,posSet,dafSet,normBin,fi):
    #奇数行为pos，偶数行为value
    nslGroupSet = np.zeros(shape=(len(nslSet),200))
    left = 0

    for idx in range(len(nslSet)):

        right = left + 1
        subIhsValue = np.asarray(nslSet[idx],dtype=float)
        subpos = np.asarray(posSet[idx],dtype=float)
        subfreD = np.asarray(dafSet[idx],dtype=float)

        posNormalize,nslNormalize = statCompute(subIhsValue,subpos,subfreD,normBin,region=200)

        nslGroupSet[left:right] = nslNormalize
        left = right

    np.savetxt(f'{str(fi)}_nslStastic', nslGroupSet)
    return 0
