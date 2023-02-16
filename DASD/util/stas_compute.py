import collections
import numpy as np
import allel
import sys
sys.path.append('..')
import multiprocessing
# 对应dihh部分，后期一起优化删除
from multiprocessing.pool import ThreadPool
# *优化为具体函数
from util.window_tools import *


######################### 表征sfs的统计量 ##################

def eng_compute(matrix):
    logp = np.log2(matrix)
    logp[np.isinf(logp)] = 0
    return np.sum(-1 * logp * matrix)

def mlevel(rank,mean,nrank,data):
    return np.sum(np.power((rank-mean),nrank)*data)

def matrix_stastic(data):
    rank = np.arange(len(data))
    mean = np.sum(rank*data)
    m2 = 1 - 1 / (1 + mlevel(rank,mean,2,data))
    m3 = mlevel(rank,mean,3,data)
    m4 = mlevel(rank,mean,4,data)
    m5 = mlevel(rank,mean,5,data)
    eng = eng_compute(data)
    return mean,m2,m3,m4,m5,eng

def sfs_compute(matrix):
    #行为单倍型
    region=10
    
    allelFreq = np.mean(matrix,axis=0)
    pos_Wp = np.zeros(region)
    #value_Wp = np.zeros(region)

    right = region + 1
    #生成200个bin
    cutdaf = [i/region for i in range(1,right)]

    #将数据放入bin内
    j=0
    for i in range(len(cutdaf)):
        cut = cutdaf[i]
        loc = (allelFreq>=j)&(allelFreq<cut)
        p = allelFreq[loc]
        #v = value[:,loc]
        if p.size != 0:
            pos_Wp[i] = len(p)
            #value_Wp[i] = v

        j=cut
    return matrix_stastic(pos_Wp/np.sum(pos_Wp))


##################### 表征sfs杂合度的统计量 #########################
def dafCompute(pos,snpMatrix):
    #添加判断是否为np.array的语句
    #输出格式：前三行依次为：postion、fre_d,fre_delta
    freD = np.mean(snpMatrix,axis=0)
    freDelta = np.abs(2 * freD - 1)
    dif_pos = np.diff(pos)
    nbase = int((np.max(pos) - np.min(pos)) / np.min(dif_pos[dif_pos > 0]))
    
    return np.sum(freDelta) / nbase

def theta_pai(snpMatrix):
    """
    pai:the mean of pairs difference
    适用于双等位基因
    """
    altFre = np.mean(snpMatrix,axis=0) 
    ancFre = 1 - altFre
    
    pi = 2 * ancFre * altFre
    return np.mean(pi)


def w_theta(pos,snpMatrix):
    """
    wtheta:
    ?????????nbase求解问题,使用100k或base数
    ???窗口大小对于sfs方法有较大影响
    """
    # n个碱基对
    #nbase = pos[-1] - pos[0] +1
    dif_pos = np.diff(pos)
    nbase = int((np.max(pos) - np.min(pos)) / np.min(dif_pos[dif_pos > 0]))

    #n条序列，segsite个分离位点
    nseq,nseg = snpMatrix.shape[0],snpMatrix.shape[1]
    an = np.sum(1/np.arange(1,nseq))
    theta = nseg / an
    #return theta / segsite
    
    return theta / nbase

def theta_H(pos, snpMatrix):
    """
    thetaH:
    nbase求解问题
    """
    dif_pos = np.diff(pos)
    nbase = int((np.max(pos) - np.min(pos)) / np.min(dif_pos[dif_pos > 0]))

    nseq = snpMatrix.shape[0]
    altFre = np.sum(snpMatrix,axis=0)
    thetaH = 2 * np.sum(altFre * altFre / (nseq * (nseq - 1)))

    return thetaH / nbase


def Fay_WusH(pos,snpMatrix):
    """
    Fay_Wu`H
    """
    return w_theta - theta_pai


def sta_base_allefre(pos,snpMatrix):
    """
    整合5个基于杂合度的统计量
    """
    
    daf = dafCompute(pos,snpMatrix)
    pai = theta_pai(snpMatrix)
    wtheta = w_theta(pos,snpMatrix)
    htheta = theta_H(pos, snpMatrix)
    h_FayWu = wtheta - pai
    
    return [daf,pai,wtheta,htheta,h_FayWu]

################### 基于单倍型的方法 ###############

def hapFreq(snpMatrix):
    """
    用于统计单倍型频率,方便后续H1、H12、H123、H2dH1、单倍型杂合度的计算
    """
    # 利用哈希值计算单倍型频率
    hash_value = [hash(tuple(i)) for i in snpMatrix]
    # 对哈希值进行统计，并根据数量做降序排列
    counts = sorted(collections.Counter(hash_value).values(), reverse=True)
    freq = np.asarray(counts) / len(hash_value)
    
    return freq

def stas_base_hapFre(snpMatrix):
    #格式检查--array
    if not isinstance(snpMatrix,np.ndarray):
        snpMatrix = np.asarray(snpMatrix,dtype='i4')
        print('Warmning: snpMatrix is not array_like,check input data!!!')

    hapNum = snpMatrix.shape[0] #单倍型数目
    
    #计算单倍型频率    
    hapFre = hapFreq(snpMatrix)
    
    #h1
    h1 = np.sum(hapFre ** 2)
    #h12
    h12 = np.sum(hapFre[:2]) ** 2 + np.sum(hapFre[2:] ** 2)
    #h123
    h123 = np.sum(hapFre[:3]) ** 2 + np.sum(hapFre[3:] ** 2)
    #h2dh1
    h2 = h1 - hapFre[0] ** 2
    h2dh1 = h2 / h1
    
    #单倍型杂合度
    hap_diversity = (1 - np.sum(hapFre ** 2)) * hapNum / (hapNum - 1)
    
    # Nhap
    Nhap = len(hapFre)
    
    return [h1,h12,h123,h2dh1,hap_diversity,Nhap]

###############################待检验########################
################ 基于EHH
### Q1:ihs、nSL部分调用allel完成，无法和自定义窗口函数组合
### Q2：dihh沿用allel框架完成计算，多出一个自定义计算函数，且无法和自定义窗口组合

def normalize(data):
    mu = np.mean(data)
    sigma = np.std(data)
    v = (data - mu) /sigma
    v[np.isnan(v)] = 0
    return v


def ihsCompute(snpMatrix,position):
    #后续可考虑传入freD
    #position中全为缺失返回-1
    freD = np.sum(snpMatrix,axis=1) / snpMatrix.shape[1]
    ihs = allel.ihs(snpMatrix, position, map_pos=None, min_ehh=0.05, min_maf=0.05, 
                include_edges=True, gap_scale=20000, max_gap=200000, is_accessible=None, use_threads=True)
    freD = freD[~np.isnan(ihs)]
    position = position[~np.isnan(ihs)]
    ihs = ihs[~np.isnan(ihs)]
    
    if len(position) > 0:
        dafBin,ihsBin,posBin = daf_Win(freD,ihs,position,region=200)
        ihsNormalize = abs(np.concatenate([normalize(vSet) for vSet in ihsBin]))
        posNormalize = np.concatenate(posBin)
    
        posNormalize,ihsNormalize = Phy_Win(posNormalize,ihsNormalize,region=200)
    else:
        posNormalize,ihsNormalize = np.array([-1]),np.array([-1])
   
    return posNormalize,ihsNormalize

def nslCompute(snpMatrix,position):
    freD = np.sum(snpMatrix,axis=1) / snpMatrix.shape[1]
    nsl = allel.nsl(snpMatrix,use_threads=True)
    
    freD = freD[~np.isnan(nsl)]
    position = position[~np.isnan(nsl)]
    nsl = nsl[~np.isnan(nsl)]
    
    if len(position) > 0:
        dafBin,nslBin,posBin = daf_Win(freD,nsl,position,region=200)
        nslNormalize = abs(np.concatenate([normalize(vSet) for vSet in nslBin]))
        posNormalize = np.concatenate(posBin)
        posNormalize,nslNormalize = Phy_Win(posNormalize,nslNormalize,region=200)
    else:
        posNormalize,nslNormalize = np.array([-1]),np.array([-1])
    
    return posNormalize,nslNormalize
    

def deltaihh(h, pos, map_pos=None, min_ehh=0.05, min_maf=0.05, include_edges=False, gap_scale=20000, max_gap=200000, is_accessible=None, use_threads=True):
    """
    沿用allel框架,略做修改
    """
    h = allel.util.asarray_ndim(h, 2)
    allel.util.check_integer_dtype(h)
    pos = allel.util.asarray_ndim(pos, 1)
    allel.util.check_dim0_aligned(h, pos)
    h = allel.compat.memoryview_safe(h)
    pos = allel.compat.memoryview_safe(pos)
    gaps = allel.stats.selection.compute_ihh_gaps(pos, map_pos, gap_scale, max_gap, is_accessible)

    kwargs = dict(min_ehh=min_ehh, min_maf=min_maf, include_edges=include_edges)
    if use_threads and multiprocessing.cpu_count() > 1:
        pool = ThreadPool(2)
        result_fwd = pool.apply_async(allel.opt.stats.ihh01_scan, (h, gaps), kwargs)
        result_rev = pool.apply_async(allel.opt.stats.ihh01_scan, (h[::-1], gaps[::-1]), kwargs)

        pool.close()
        pool.join()
        ihh0_fwd, ihh1_fwd = result_fwd.get()
        ihh0_rev, ihh1_rev = result_rev.get()
        pool.terminate()
    else:
        ihh0_fwd, ihh1_fwd = allel.opt.stats.ihh01_scan(h, gaps, **kwargs)
        ihh0_rev, ihh1_rev = allel.opt.stats.ihh01_scan(h[::-1], gaps[::-1], **kwargs)
    ihh0_rev = ihh0_rev[::-1]
    ihh1_rev = ihh1_rev[::-1]
    ihh0 = ihh0_fwd + ihh0_rev
    ihh1 = ihh1_fwd + ihh1_rev
    return np.abs(ihh1 - ihh0)

def dihhCompute(snpMatrix,position):
    freD = np.sum(snpMatrix,axis=1) / snpMatrix.shape[1]
    score = deltaihh(snpMatrix, position, map_pos=None, min_ehh=0.05, min_maf=0.05, 
                include_edges=True, gap_scale=20000, max_gap=200000, is_accessible=None, use_threads=True)
    freD = freD[~np.isnan(score)]
    position = position[~np.isnan(score)]
    dihh = score[~np.isnan(score)]
    
    if len(position) > 0:
        dafBin,dihhBin,posBin = daf_Win(freD,dihh,position,region=200)
        dihhNormalize = abs(np.concatenate([normalize(vSet) for vSet in dihhBin]))
        posNormalize = np.concatenate(posBin)
    
        posNormalize,dihhNormalize = Phy_Win(posNormalize,dihhNormalize,region=200)
    else:
        posNormalize,dihhNormalize = np.array([-1]),np.array([-1])
   
    return posNormalize,dihhNormalize

############################基于溯祖的方法#######################
def HAF(snpMatrix):
    return np.dot(snpMatrix,np.transpose(snpMatrix)).sum(1)

def sum_sta(data):
    #data每组数据以行排序（即组内元素写入一行）
    if data.ndim != 2:
        sys.exit("dim is not equal 2")
    
    datamax = np.max(data,axis=1)
    dataMean = np.mean(data,axis=1)
    datavar = np.var(data,axis=1)
    dataskew = np.mean((data-dataMean.reshape(-1,1)) ** 3,axis=1)
    datakurt = np.mean((data - dataMean.reshape(-1,1)) ** 4,axis=1)

    return np.array([datamax,dataMean,datavar,np.abs(dataskew),datakurt]).T

def safecompute(snpMatrix):
    """代码来自于safeclass"""
    ## ERROR snpMatrix 不应转置
    snpMatrix = snpMatrix.T
    haf = np.dot(snpMatrix,snpMatrix.T).sum(1)
    haf_matrix = haf.reshape(-1,1) * snpMatrix
    K = np.zeros(snpMatrix.shape[1])
    for j in range(len(K)):
        ar = haf_matrix[:,j]
        K[j] = len(np.unique(ar[ar>0]))
    H = np.sum(haf_matrix,0)

    phi = H/sum(haf)
    kappa = K/np.unique(haf).shape[0]

    freq = snpMatrix.mean(0)
    sigma = kappa * (1-kappa)
    sigma[sigma == 0] = 1.0
    sigma = sigma ** 0.5
    p1 = (phi - kappa) / sigma

    sigma2 = freq * (1-freq)
    sigma2[sigma2 == 0] = 1.0
    sigma2 = sigma2 ** 0.5
    p2 = (phi - kappa) / sigma2

    nu = freq[np.argmax(p1)]
    safe = p1*(1-nu) + p2*nu

    return kappa,phi,safe

