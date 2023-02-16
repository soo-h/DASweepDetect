
# 后续修改*，具体到载入的函数
## 若仅用于ms_read_pipline 接口则无需增加检查函数

from util import stas_compute
from util.stas_compute import *
from util.tools_windows import *

## region参数--- 决定特征图size
def write_stats(data_generator, fi,stats, gridNum, snpNum):
    """
    组合统计量函数和自定义滑窗函数,完成除沿用allele框架外的EHH方法外其它方法的生成与整合
    用于真实数据,和ms的区别在于phy_win的划分方式,即增加了vector_loc和Phy_Win部分
    """
    ## 仅保存value信息
    with open(fi,'w') as f:
        for snpMatrix,position in data_generator:

            stasSet, position = dropgrid_statComput(stats, snpMatrix, position, \
                gridNum=gridNum, snpNum=snpNum, edge=False)

            position, stasSet = Phy_Win(position, stasSet,region=200)

            for stas in stasSet:
                f.write('\t'.join([str(v) for v in stas]) + '\n')
    return 0


def write_sfs(data_generator,fi,gridNum=200,snpNum=50):
    name = f'{fi}_sfsStastic'
    write_stats(data_generator,name,stas_compute.sfs_compute,gridNum,snpNum)
    return 0

def write_hapFre(data_generator,fi,gridNum=200,snpNum=50):
    name = f'{fi}_hapFrebaseStastic'
    write_stats(data_generator,name,stas_compute.stas_base_hapFre,gridNum,snpNum)
    return 0

def write_allelFre(data_generator,fi,gridNum=200,snpNum=50):
    name = f'{fi}_allelFrebaseStastic'
    write_stats(data_generator,name,stas_compute.sta_base_allefre,gridNum,snpNum)
    return 0



def write_ihs(data_generator,fi):
    L = 100000
    #
    fi = f'{str(fi)}_ihsStastic'
    with open(fi,'w') as f:
        for snpMatrix,position in data_generator:

            snpMatrix = np.transpose(snpMatrix)
            position = position * L
            posNormalize,ihsNormalize = ihsCompute(snpMatrix,position)

            f.write('\t'.join([str(v) for v in ihsNormalize]) + '\n')

    return 0

def write_nsl(data_generator,fi):
    L = 100000
    #
    fi = f'{str(fi)}_nslStastic'
    with open(fi,'w') as f:
        for snpMatrix,position in data_generator:

            snpMatrix = np.transpose(snpMatrix)
            position = position * L
            posNormalize,nslNormalize = nslCompute(snpMatrix,position)

            f.write('\t'.join([str(v) for v in nslNormalize]) + '\n')

    return 0

def write_dihh(data_generator,fi):
    L = 100000
    #
    fi = f'{str(fi)}_dihhStastic'
    with open(fi,'w') as f:
        for snpMatrix,position in data_generator:

            snpMatrix = np.transpose(snpMatrix)
            position = position * L
            posNormalize,dihhNormalize = dihhCompute(snpMatrix,position)

            f.write('\t'.join([str(v) for v in dihhNormalize]) + '\n')

    return 0


def write_safe(data_generator,fi,gridNum=200,snpNum=50):
    f1 = open(f'{str(fi)}_kappa','w')
    f2 = open(f'{str(fi)}_phi','w')
    f3 = open(f'{str(fi)}_safe','w')

    for snpMatrix,position in data_generator:
        safeGroup,posGroup = dropgrid_statComput(safecompute,snpMatrix,\
            position,gridNum=gridNum,snpNum=snpNum,edge=False)
        kappa = safeGroup[:,0,:]
        phi = safeGroup[:,1,:]
        safe = safeGroup[:,2,:]

        kappa_sum,phi_sum,safe_sum = sum_sta(kappa),sum_sta(phi),sum_sta(safe)


        pos1,kappa_sum = Phy_Win(posGroup,kappa_sum)
        pos2,phi_sum = Phy_Win(posGroup,phi_sum)
        pos3,safe_sum = Phy_Win(posGroup,safe_sum)

        for i in range(kappa_sum.shape[0]):
            f1.write('\t'.join([str(v) for v in kappa_sum[i]]) + '\n')
            f2.write('\t'.join([str(v) for v in phi_sum[i]]) + '\n')
            f3.write('\t'.join([str(v) for v in safe_sum[i]]) + '\n')
    
    return 0

def write_haf(data_generator,fi,gridNum=200,snpNum=50):
    fi = f'{fi}_HAFStastic'

    f = open(fi,'w')
    for snpMatrix,position in data_generator:
        hafGroup,posGroup = dropgrid_statComput(stas_compute.HAF,snpMatrix,\
            position,gridNum=gridNum,snpNum=snpNum,edge=False)

        haf_sum = sum_sta(hafGroup)
        pos,haf_sum = Phy_Win(posGroup,haf_sum)
        
        for stas in haf_sum:
            f.write('\t'.join([str(v) for v in stas]) + '\n')
    
    return 0
