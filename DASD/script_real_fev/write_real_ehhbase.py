import numpy as np
import sys
sys.path.append('..')
from util import window_tools


def normBin(filtpos,staValue,freD):
    freD_dropna = freD[~np.isnan(staValue)]
    filtpos_dropna = np.asarray(filtpos)[~np.isnan(staValue)]
    staValue_dropna = staValue[~np.isnan(staValue)]
    dafBin,ihsBin,posBin = window_tools.daf_Win(freD_dropna,staValue_dropna,filtpos_dropna,region=200)
    ihsBin = [(np.mean(Bin),np.std(Bin)) for Bin in ihsBin]
    return ihsBin

def norm_by_daf(ihsBin,normBin):
    for idx in range(len(ihsBin)):
        if len(ihsBin[idx]):
            if not np.sum(np.isnan(normBin[idx])):
                ihsBin[idx] = (ihsBin[idx] - normBin[idx][0]) / normBin[idx][1]
            else:
                sys.exit('region and entirety not compaer!!!')
    ihsBin = np.abs(np.concatenate(ihsBin))
    return ihsBin

def statCompute(subStatValue,subpos,subfreD,normBin,region=200):
    locs = window_tools.vector_loc(subpos,region)
    subfreD = subfreD[~np.isnan(subStatValue)]
    subpos = subpos[~np.isnan(subStatValue)]
    subStatValue = subStatValue[~np.isnan(subStatValue)]
    if len(subpos) > 0:
        dafBin,ihsBin,posBin = window_tools.daf_Win(subfreD,subStatValue,subpos,region)
        ihsNormalize = norm_by_daf(ihsBin,normBin)
        posNormalize = np.concatenate(posBin)
    

        posNormalize,ihsNormalize = window_tools.Phy_Win_real(posNormalize,ihsNormalize,locs)
    else:
        posNormalize,ihsNormalize = np.array([-1]),np.array([-1])

    return posNormalize,ihsNormalize




import copy

def normalize(data):
    mu = np.mean(data)
    sigma = np.std(data)
    return (data - mu) /sigma



def normBin2(filtpos,staVal,freD):
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


def write_ihs(ihsSet,posSet,dafSet,normBin,fi):
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
