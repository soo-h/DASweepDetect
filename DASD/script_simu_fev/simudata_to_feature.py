import multiprocessing
import subprocess
import Data_To_Feature_pipline
from util.window_tools import ms_read_pipline
import sys
import time
import numpy as np
import os
from tools_feature import loadstastic
import warnings
import copy
warnings.filterwarnings("ignore")

## 1. 对比基于生成器 、数据流、原脚本间性能

## 优化方式：将数据读取为生成器(利用yield)
## 优化结果,原策略每个并行使用6G内存，优化后，每个并行使用2G内存

nameSet = sys.argv[1].split(',')


coreNum = int(sys.argv[2])

cutoff = int(sys.argv[3])
outdir = sys.argv[4]
if not outdir.endswith('/'):
    outdir = f'{str(outdir)}/'



# 模型训练所需最小样本数---待定
min_sample = 3000

def iter_file(fileSet):
    ljl = iter(fileSet)
    while True:
        try:
            yield(next(ljl))
        except Exception:
            break
    yield "finish0"


def drop_sample(file,segsiteSet,hapSet,posSet,cutoff):
    """
    drop sample by SNP number, if sample contain SNPs < cutoff
    """
    hapSet_filter = []
    posSet_filter = []

    for i in range(len(segsiteSet)):
        if segsiteSet[i] >= cutoff:
            hapSet_filter.append(np.asarray(hapSet[i]))
            posSet_filter.append(np.asarray(posSet[i]))

    print(f'After filter: {file} contain {len(hapSet)} samples !!')
    #return iter(hapSet_filter),iter(posSet_filter)
    return hapSet_filter,posSet_filter

def para_run(process_query,coreNum):
    process_running = []
    
    for _ in range(coreNum):
        p = next(process_query)
        process_running.append(p)
        p.start()

    while True:
        fin = False
        time.sleep(10)
        ## 入队
        while sum(p.is_alive() for p in process_running) < coreNum:
            ## 中止结束的进程
            for _ in process_running:
                if not _.is_alive():
                    _.terminate()
            try:
                p = next(process_query)
            except Exception:
                fin = True
                break

            process_running.append(p)
            p.stsart()

        if fin:
            break

    ## 等待任务子进程结束
    while sum(p.is_alive() for p in process_running) != 0:
        time.sleep(10)
    return 0



def calc_stastic_simu(file,coreNum,cutoff,opt):
    """
    未判断用户是否有足够的cpu进行并行
    """
    #name = file.split('/')[-1]
    #opt = outdir + name

    data_generator = window_tools.ms_read_pipline(file,cutoff)

    haf_ = multiprocessing.Process(target=Data_To_Feature_pipline.write_haf,args=(data_generator,opt))
    sfs_ = multiprocessing.Process(target=Data_To_Feature_pipline.write_sfs, args=(data_generator,opt))
    hapFre_ = multiprocessing.Process(target=Data_To_Feature_pipline.write_hapFre, args=(data_generator,opt))
    alleFre_ = multiprocessing.Process(target=Data_To_Feature_pipline.write_allelFre,args=(data_generator,opt))
    ihs_ = multiprocessing.Process(target=Data_To_Feature_pipline.write_ihs, args=(data_generator,opt))
    nsl_ = multiprocessing.Process(target=Data_To_Feature_pipline.write_nsl, args=(data_generator,opt))
    safe_ = multiprocessing.Process(target=Data_To_Feature_pipline.write_safe,args=(data_generator,opt))
    ihh_ = multiprocessing.Process(target=Data_To_Feature_pipline.write_dihh,args=(data_generator,opt))

    process_query = iter([haf_,safe_,ihh_,ihs_,nsl_,sfs_,hapFre_,alleFre_])
 

    _ = para_run(process_query,coreNum)

    return 0

def get_featureMap(file,coreNum,cutoff,outdir):
    #remain = True
    name = file.split('/')[-1]
    opt = outdir + name
    _ = calc_stastic_simu(file,coreNum,cutoff,opt)
    
    ## 整理生成特征图
    featureNameSet = [outdir + caluc_name for caluc_name in os.listdir(outdir) if caluc_name.startswith(name)]
    featureMap = loadstastic(copy.deepcopy(featureNameSet))
    
    #if not remain
    ## 删除中间文件
    cmd = 'rm -f ' + ' '.join(featureNameSet)
    print(cmd)
    subprocess.call(cmd,shell=True)
    ## 保存特征图
    np.save(f'{opt}_featureMap',featureMap)
    return 0




### 优化方式：不考虑进程，仅考虑剩余核数。
## 1.剩余 >=8,进程中传8个CPU；小于8，传入剩余CPU
## 2.等待CPU空闲
## 重复1.2. 直至无文件

fileNum = len(nameSet)
if coreNum > 8 * fileNum:
    print(f'Warning: too much cpu!! Recommend {8 * fileNum}')

if coreNum > 8:
    ## 进程间并行,进程内并行
    process_Mcore_number = coreNum / 8
    core_residue = coreNum % 8

    file_iter = iter_file(nameSet)
    processSet = []
    process_residu = None
    while True:
        run = 0

        if not processSet:
            run = 1
            runing_number = 0
        else:
            runing_number = np.sum([p.is_alive() for p in processSet])
            if runing_number < process_Mcore_number:
                run = 1

        pre_run_number = int(process_Mcore_number - runing_number)
        
        if run == 1:
            ## 用8个cpu执行进程
            for _ in range(pre_run_number):
                file = next(file_iter)
                if file == "finish0":
                    run = -1
                    break

                p = multiprocessing.Process(target=get_featureMap, args=(file,8,cutoff,outdir))
                p.start()
                processSet.append(p)
            ## 若无待运行进程，中止
            if run == -1:
                break


        if (process_residu and not process_residu.is_alive() \
            or not process_residu):

            file = next(file_iter)
            ## 若无待运行进程，中止
            if file == "finish0":
                break
            
            process_residu = multiprocessing.Process(target=get_featureMap, args=(file,core_residue,cutoff,outdir))
            process_residu.start()

else:
    ## 进程间串行
    for file in nameSet:
        get_featureMap(file,coreNum,cutoff)
