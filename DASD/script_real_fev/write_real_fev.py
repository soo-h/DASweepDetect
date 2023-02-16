import multiprocessing
import numpy as np
import sys
sys.path.append('..')
from util import window_tools
from util.stas_compute import *
from util import stas_compute
import allel
from script_real_fev import write_real_ehhbase


def write_stats_real(data_generator, fi,stats, gridNum, snpNum):
    """
    组合统计量函数和自定义滑窗函数,完成除沿用allele框架外的EHH方法外其它方法的生成与整合
    用于真实数据,和ms的区别在于phy_win的划分方式,即增加了vector_loc和Phy_Win部分
    """

    with open(fi,'w') as f:
        for snpMatrix,position in data_generator:
            locs = window_tools.vector_loc(position,region=200)
            stas, position = window_tools.dropgrid_statComput(stats, snpMatrix, position, gridNum=gridNum, snpNum=snpNum, edge=False)
            position, stasSet = window_tools.Phy_Win_real(position, stas, locs)
            
            for stas in stasSet:
                f.write('\t'.join([str(v) for v in stas]) + '\n')
    return 0


def write_sfs(data_generator,fi,gridNum=200,snpNum=50):
    name = f'{fi}_sfsStastic'
    write_stats_real(data_generator,name,stas_compute.sfs_compute,gridNum,snpNum)
    return 0

def write_hapFre(data_generator,fi,gridNum=200,snpNum=50):
    name = f'{fi}_hapFrebaseStastic'
    write_stats_real(data_generator,name,stas_compute.stas_base_hapFre,gridNum,snpNum)
    return 0

def write_allelFre(data_generator,fi,gridNum=200,snpNum=50):
    name = f'{fi}_allelFrebaseStastic'
    write_stats_real(data_generator,name,stas_compute.sta_base_allefre,gridNum,snpNum)
    return 0


def write_haf(data_generator,fi,gridNum=200,snpNum=50):

    fi = f'{fi}_HAFStastic'

    f = open(fi,'w')
    for snpMatrix,position in data_generator:
        locs = window_tools.vector_loc(position,region=200)
        hafGroup,posGroup = window_tools.dropgrid_statComput(stas_compute.HAF,snpMatrix,\
            position,gridNum=gridNum,snpNum=snpNum,edge=False)

        haf_sum = sum_sta(hafGroup)
        pos,haf_sum = window_tools.Phy_Win_real(posGroup,haf_sum,locs)
        
        for stas in haf_sum:
            f.write('\t'.join([str(v) for v in stas]) + '\n')
    
    return 0


def write_safe(data_generator,fi,gridNum=200,snpNum=50):
    """
    snpMatrix : nhap,nvariance
    
    """
    f1 = open(f'{str(fi)}_kappa','w')
    f2 = open(f'{str(fi)}_phi','w')
    f3 = open(f'{str(fi)}_safe','w')

    for snpMatrix,position in data_generator:
        locs = window_tools.vector_loc(position,region=200)
        safeGroup,posGroup = window_tools.dropgrid_statComput(stas_compute.safecompute,snpMatrix,\
            position,gridNum=gridNum,snpNum=snpNum,edge=False)

        kappa = safeGroup[:,0,:]
        phi = safeGroup[:,1,:]
        safe = safeGroup[:,2,:]


        kappa_sum,phi_sum,safe_sum = \
            sum_sta(kappa),sum_sta(phi),sum_sta(safe)
        
        pos1,kappa_sum = window_tools.Phy_Win_real(posGroup,kappa_sum,locs)
        pos2,phi_sum = window_tools.Phy_Win_real(posGroup,phi_sum,locs)
        pos3,safe_sum = window_tools.Phy_Win_real(posGroup,safe_sum,locs)

        for i in range(len(kappa_sum)):
            f1.write('\t'.join([str(v) for v in kappa_sum[i]]) + '\n')
            f2.write('\t'.join([str(v) for v in phi_sum[i]]) + '\n')
            f3.write('\t'.join([str(v) for v in safe_sum[i]]) + '\n')

    return 0

def write_standard_EHHbase(snpMatrix, filtpos,win_loc,tolearance,fi):
    ihs = allel.ihs(snpMatrix, filtpos,map_pos=None, min_ehh=0.05, min_maf=0.05, \
        include_edges=False, gap_scale=20000, max_gap=200000, is_accessible=None, use_threads=True)
    
    nsl = allel.nsl(snpMatrix,use_threads=True)

    dihh = stas_compute.deltaihh(snpMatrix, filtpos, map_pos=None, min_ehh=0.05, min_maf=0.05,include_edges=False, \
        gap_scale=20000, max_gap=200000, is_accessible=None, use_threads=True)

    freD = np.sum(snpMatrix,axis=1) / snpMatrix.shape[1]

    dafSet = []
    ihsSet = []
    nslSet = []
    dihhSet = []
    posSet = []
    ### 参数3---过滤区域条件
    for loc in win_loc:
        if loc[1] - loc[0] >= tolearance:
            # varience,hap
            # 后续使用dataSet需注意shape是否匹配
            dafSet.append(freD[loc[0]:loc[1]])
            ihsSet.append(ihs[loc[0]:loc[1]])
            nslSet.append(nsl[loc[0]:loc[1]])
            dihhSet.append(dihh[loc[0]:loc[1]])
            posSet.append(filtpos[loc[0]:loc[1]])
    ######获取标准化信息
    ihsNormBin = write_real_ehhbase.normBin(filtpos,ihs,freD)
    nslNormBin = write_real_ehhbase.normBin(filtpos,nsl,freD)
    dihhNormBin = write_real_ehhbase.normBin(filtpos,dihh,freD)


    ihs1_ = multiprocessing.Process(target=write_real_ehhbase.write_ihs, args=(ihsSet,posSet,dafSet,ihsNormBin,fi))
    nsl1_ = multiprocessing.Process(target=write_real_ehhbase.write_nsl, args=(nslSet,posSet,dafSet,nslNormBin,fi))
    ihh1_ = multiprocessing.Process(target=write_real_ehhbase.write_dihh,args=(dihhSet,posSet,dafSet,dihhNormBin,fi))

    for p in [ihs1_,nsl1_,ihh1_]:
        p.start()
        p.join()
        p.terminate()
