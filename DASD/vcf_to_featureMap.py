import numpy as np
import sys
from script_real_fev import readtools 
from script_real_fev import write_real_fev
import multiprocessing 
from util import window_tools
import time
import os
from util.tools_feature import loadstastic
import subprocess
import warnings
import copy
warnings.filterwarnings("ignore")




nameSet = sys.argv[1]
coreNum = int(sys.argv[2])
tolearance = int(sys.argv[3])
start_position = sys.argv[4]
end_position = sys.argv[5]
window_size = int(sys.argv[6])
window_step = sys.argv[7]
outdir = sys.argv[8]



## check input is directory
if os.path.isdir(nameSet):
    if not nameSet.endswith('/'):
        dirpath = nameSet + '/'
    else:
        dirpath = nameSet

    nameSet = [dirpath + name for name in os.listdir(dirpath)] 
    if len(nameSet) != np.sum([True for n in nameSet if n.endswith('.vcf.gz') or n.endswith('.vcf')]):
        print("Error:The files in the input folder must be .vcf or .vcf.gz files.")
        sys.exit(1)

else:
    nameSet = nameSet.split(',')

if not outdir.endswith('/'):
    outdir = f'{str(outdir)}/'


def check_region_paramater(position):
    if position == "None":
        position = None
    else:
        position = int(position)

    return position

def check_step(step,window_size):
    if step == "None":
        step = int(window_size / 20)
    else:
        step = int(step)
    return step

if len(nameSet) > 1:
    try:
        start_position == end_position == "None"
    except Exception as e:
        print("Error:The start and stop sites are not allowed \
            when multiple VCF files are passed into the program!!!. ")


def real_data_generator(dataSet,posSet):
    assert len(dataSet) == len(posSet)
    for i in range(len(posSet)):
        yield (np.asarray(dataSet[i]),np.asarray(posSet[i]))

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
            p.start()

        if fin:
            break

    ## 等待任务子进程结束
    while sum(p.is_alive() for p in process_running) != 0:
        time.sleep(10)
    return 0

def iter_file(fileSet):
    ljl = iter(fileSet)
    while True:
        try:
            yield(next(ljl))
        except Exception:
            break
    yield "finish0"

def save_position(posSet,opt):
    opt = f'{opt}posInfo'
    with open(opt,'w') as f:
        _ = [f.write(str(_[0])+'\t'+str(_[-1])+'\n') for _ in posSet]
    return 0


def calc_stastic_real(file,coreNum,tolearance,start_position,end_position,window_size,window_step,opt):

    start_position = check_region_paramater(start_position)
    end_position = check_region_paramater(end_position)
    window_step = check_step(window_step,window_size)

    ## 优化1，不需要全部读取
    #snpMatrix,filtpos = readtools.vcf_to_matrix_pos(file)
    snpMatrix,filtpos = readtools.vcf_to_matrix_pos(file,start_position,end_position)
    ##snpMatrix的shape：(varience,hap)
    window = window_tools.position_windows(filtpos,window_size, start=start_position,stop=end_position,step=window_step)
    win_loc = window_tools.window_loc(filtpos, window)

    dataSet = [snpMatrix[loc[0] : loc[1]].T for loc in win_loc if loc[1] - loc[0] >= tolearance]
    posSet = [filtpos[loc[0]:loc[1]] for loc in win_loc if loc[1] - loc[0] >= tolearance]
    # 保存位置信息
    save_position(posSet,opt)
    ## 统计量计算
    data_generator = real_data_generator(dataSet,posSet)

    sfs_ = multiprocessing.Process(target=write_real_fev.write_sfs, args=(data_generator, opt))
    hapFre_ = multiprocessing.Process(target=write_real_fev.write_hapFre, args=(data_generator, opt))
    alleFre_ = multiprocessing.Process(target=write_real_fev.write_allelFre,args=(data_generator, opt))
    safe_ = multiprocessing.Process(target=write_real_fev.write_safe,args=(data_generator, opt))
    haf_ = multiprocessing.Process(target=write_real_fev.write_haf,args=(data_generator, opt))   
    ehh_base = multiprocessing.Process(target=write_real_fev.write_standard_EHHbase,args=(snpMatrix, filtpos,win_loc,tolearance,opt))

    process_query = iter([ehh_base,haf_,safe_,sfs_,hapFre_,alleFre_])

    _ = para_run(process_query,coreNum)
    return 0


def get_featureMap(file,coreNum,tolearance,start_position,end_position,window_size,window_step,outdir):
    #remain = True
    name = file.split('/')[-1]
    if name.endswith('gz'):
        name = name[:-3]
    opt = outdir + name
    _ = calc_stastic_real(file,coreNum,tolearance,start_position,end_position,window_size,window_step,opt)
    
    ## 整理生成特征图
    featureNameSet = [outdir + caluc_name for caluc_name in os.listdir(outdir) if caluc_name.startswith(f'{name}_')]
    featureMap = loadstastic(copy.deepcopy(featureNameSet))
    
    #if not remain
    ## 删除中间文件
    cmd = 'rm -f ' + ' '.join(featureNameSet)
    subprocess.call(cmd,shell=True)

    ## 保存特征图
    np.save(f'{opt}_featureMap',featureMap)
    return 0





core_one_process = 6
fileNum = len(nameSet)
if coreNum > core_one_process * fileNum:
    print(f'Warning: too much cpu!! Recommend {core_one_process * fileNum}')

if coreNum > core_one_process:
    ## 进程间并行,进程内并行
    process_Mcore_number = coreNum / core_one_process
    core_residue = coreNum % core_one_process

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

                p = multiprocessing.Process(target=get_featureMap, args=(file,core_one_process,tolearance,start_position,end_position,window_size,window_step,outdir))
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
            
            process_residu = multiprocessing.Process(target=get_featureMap, args=(file,core_residue,tolearance,start_position,end_position,window_size,window_step,outdir))
            process_residu.start()

else:
    ## 进程间串行
    for file in nameSet:
        get_featureMap(file,coreNum,tolearance,start_position,end_position,window_size,window_step,outdir)
