
# 后续修改*，具体到载入的函数
## 若仅用于ms_read_pipline 接口则无需增加检查函数

from util import stas_compute
from util.stas_compute import *
from util.window_tools import *
import time
import os

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

###################### EHH方法
def ehh_base_unstandard(ipt_name,cutoff,opt_name,stas):

    L = 100000

    with open(opt_name,'w') as f:
        f.write("Value\tPosition\tFreq\n")
        data_generator = ms_read_pipline(ipt_name,cutoff)
        
        value_number_each_sample = [] # save SNP number of each sample
        for snpMatrix,position in data_generator:
            snpMatrix = np.transpose(snpMatrix)
            if stas.__name__ != 'nsl':
                value = stas(snpMatrix,position*L,min_ehh=0.05,min_maf=0.05,include_edges=True,gap_scale=20000,max_gap=200000,is_accessible=None,use_threads=True)
                #value = stas(snpMatrix,position*L,min_ehh=0.05,min_maf=0.05,include_edges=False,gap_scale=20000,max_gap=200000,is_accessible=None,use_threads=True)
            else:
                value = stas(snpMatrix,use_threads=True)
            freD = np.sum(snpMatrix,axis=1) / snpMatrix.shape[1]   
    
            ## drop NA
            freD = freD[~np.isnan(value)]
            position = position[~np.isnan(value)]
            value = value[~np.isnan(value)]
        
            value_number_each_sample.append(str(len(position)))
        
            _ = [f.write('\t'.join([str(value[idx]),str(position[idx]),str(freD[idx])]) + '\n') for idx in range(len(freD))]
    
        f.write('value_number_each_sample:\n') 
        f.write('\t'.join(value_number_each_sample))
    return 0

def read_ehh_base_summary_File(file):
    with open(file,'r') as f:
        _ = f.readline()
        value = []
        fred = []
        while True:
            line = f.readline().strip()
            if line.startswith('value_number_each_sample'):
                break
            else:
                line = line.split('\t')
                value.append(float(line[0]))
                fred.append(float(line[-1]))
        return value,fred

def normalize(data):
    mu = np.mean(data)
    sigma = np.std(data)

    return (mu,sigma)
    
    
def compute_Norm_info(daf,value,region=50):
    daf_Pw = []
    fre_d_Wp = []

    daf = np.array(daf)
    value = np.array(value)

    region = int(region)
    right = region + 1
    #生成50个bin
    cutdaf = [i/region for i in range(1,right)]

    #将数据放入bin内
    j=0
    for i in cutdaf:
        idx = (daf >= j) & (daf < i)
        daf_Pw.append(daf[idx])
        fre_d_Wp.append(value[idx])
        j = i
    norm = [normalize(vSet) for vSet in fre_d_Wp]
    return norm


def getNorm_info(summary_file): 
    
    valueSet = []
    dafSet = []
    
    for file in summary_file:
        value,fred = read_ehh_base_summary_File(file)
        valueSet.append(value)
        dafSet.append(fred)


    valueSet = np.concatenate(valueSet)
    dafSet = np.concatenate(dafSet)

    norm_info_base_freq = compute_Norm_info(dafSet,valueSet,region=50)
    return norm_info_base_freq


def standard_ehhbase(norm_info_base_freq,fred,value,region):
    region = int(region) 
    query = np.arange(1,region+1) / region
    idx = np.searchsorted(query,fred)
    miu,std = norm_info_base_freq[idx]
    value_standard = (value - miu) / std
    return value_standard


def get_standard_ehhbase(file,norm_info_base_freq,region=50):
    value_standardSet = []
    posSet = []
    
    with open(file,'r') as f:
        _ = f.readline()
        while True:
            line = f.readline().strip()
            if line.startswith('value_number_each_sample'):
                break
            else:
                line = line.split('\t')
                value = float(line[0])
                pos = float(line[1])
                fred = float(line[2])
                
                value_standard = standard_ehhbase(norm_info_base_freq,fred,value,region)
        
                value_standardSet.append(value_standard)
                posSet.append(pos)
        sampleInfo = [int(s) for s in f.readline().strip().split()]
    
    
    return value_standardSet,posSet,sampleInfo


def out_standard_EHHbase(file,norm_info_base_freq,opt):
    vector_len = 200
    value_standardSet,posSet,sampleInfo = get_standard_ehhbase(file,norm_info_base_freq)
    left = 0
    with open(opt,'w') as f:
        for right in np.cumsum(sampleInfo):
            sample_value = np.abs(value_standardSet[left:right])
            sample_pos = np.asarray(posSet[left:right])

            if len(sample_pos) > 0:
                sample_pos,sample_value = Phy_Win(sample_pos,sample_value,region=200)
            else:
                sample_pos,sample_value = -np.ones(vector_len),-np.ones(vector_len)
            f.write('\t'.join([str(v) for v in sample_value]) + '\n')
            left = right
    return 0


def out_EHHbase_pipline(nameSet,cutoff,outdir,stas,stas_key_word,coreNum):
    summary_name_key_word = f'{stas_key_word}_summaryInfo'
    
    process = []
    for ipt in nameSet:
        name = ipt.split('/')[-1]
        opt_name = f'{outdir}{name}{summary_name_key_word}'
        p = multiprocessing.Process(target=ehh_base_unstandard,args=([ipt,cutoff,opt_name,stas]))
        process.append(p)
        p.start()
    while np.sum([p.is_alive() for p in process]) != 0:
        time.sleep(10)
    _ = [p.terminate() for p in process]
        
    summary_fileName = [name for name in os.listdir(outdir) if  name.endswith(summary_name_key_word)] 
    summary_fileSet = [f'{outdir}{name}' for name in summary_fileName] 

    #summary_fileSet = [f'{outdir}{name}' for name in os.listdir(outdir) if  name.endswith(summary_name_key_word)] 
        
    norm_info_base_freq = getNorm_info(summary_fileSet)

######改(2023.2.20注):1.将core作为write接口函数，优化core和进程的关系;2.串行视为core=1，从而将if else优化掉
    process = []
    for i in range(len(summary_fileSet)):
        summary_path = summary_fileSet[i]
        summary_name = summary_fileName[i]
        #ipt = nameSet[i]
        #name = ipt.split('/')[-1]
        
        name = summary_name.split(stas_key_word)[0]#修改原因：nameSet和summary_fileSet间并非一一对应关系（修改日期：2023.2.24）
        opt = f'{outdir}{name}_{stas_key_word}Stastic'
        if coreNum == 4:
            p = multiprocessing.Process(target=out_standard_EHHbase,args=([summary_path,norm_info_base_freq,opt]))
            p.start()
            process.append(p)

        else:
            out_standard_EHHbase(summary_path,norm_info_base_freq,opt)
    
    if len(process) > 0:
        while np.sum([p.is_alive() for p in process]) != 0:
            time.sleep(10)
######################### 需优化部分截至线(还有write接口和主函数中的args参数)################
    return 0

def write_ihs(nameSet,cutoff,outdir):
    coreNum = 4
    stas_key_word = 'ihs'
    stas = allel.ihs
    out_EHHbase_pipline(nameSet,cutoff,outdir,stas,stas_key_word,coreNum)
    return 0


def write_nsl(nameSet,cutoff,outdir):
    coreNum = 4
    stas_key_word = 'nsl'
    stas = allel.nsl
    out_EHHbase_pipline(nameSet,cutoff,outdir,stas,stas_key_word,coreNum)
    return 0

def write_dihh(nameSet,cutoff,outdir):
    coreNum = 4
    stas_key_word = 'dihh'
    stas = deltaihh
    out_EHHbase_pipline(nameSet,cutoff,outdir,stas,stas_key_word,coreNum)
    return 0