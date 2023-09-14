import sys
import multiprocessing
import time
import os
import subprocess
import warnings
import copy

import setproctitle
setproctitle.setproctitle("DASDC")
import numpy as np

from script_real_fev import readtools
from script_real_fev import write_real_fev
from util import window_tools
from util.tools_feature import loadstastic
from util.check_tools import check_region_paramater, check_step
from util.process_control import para_run, process_saver

warnings.filterwarnings("ignore")


def real_data_generator(dataSet,posSet):
    assert len(dataSet) == len(posSet)
    for i in range(len(posSet)):
        yield (np.asarray(dataSet[i]),np.asarray(posSet[i]))

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

def get_opt_name(outdir,file):

    opt = outdir + file.split('/')[-1]
    
    if opt.endswith('.gz'):
        opt = opt[:-3]
    return opt

def calc_stastic_real(file,coreNum,tolearance,start_position,end_position,window_size,window_step,opt):

    start_position = check_region_paramater(start_position)
    end_position = check_region_paramater(end_position)
    window_step = check_step(window_step,window_size)


    snpMatrix,filtpos = readtools.vcf_to_matrix_pos(file,start_position,end_position)

    window = window_tools.position_windows(filtpos,window_size, start=start_position,stop=end_position,step=window_step)
    win_loc = window_tools.window_loc(filtpos, window)


    posSet = [filtpos[loc[0]:loc[1]] for loc in win_loc if loc[1] - loc[0] >= tolearance]

    # check snp density
    if len(posSet) == 0:
        sys.exit("Error: All segments are filtered, try increasing the parameter of --window-size!!!")

    dataSet = [snpMatrix[loc[0] : loc[1]].T for loc in win_loc if loc[1] - loc[0] >= tolearance]
    # save pos information
    save_position(posSet,opt)
    # statistic calculation
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

def get_featureMap(file, outdir):
    #remain = True    
    name = file.split('/')[-1]
    if name.endswith('.gz'):
        name = name[:-3]
    opt = outdir + name
    
    # feature map  generation
    featureNameSet = [outdir + caluc_name for caluc_name in os.listdir(outdir) if caluc_name.startswith(f'{name}_')]
    featureMap = loadstastic(copy.deepcopy(featureNameSet))
    
    #if not remain, delete intermediate file
    cmd = 'rm -f ' + ' '.join(featureNameSet)
    subprocess.call(cmd,shell=True)

    # save feature map
    np.save(f'{opt}_featureMap',featureMap)
    return 0

def process_scheduling():
    
    fileNum = len(nameSet)
    core_one_process = 6
    process_info = process_saver()
    file_iter = iter_file(nameSet)

    if coreNum > core_one_process * fileNum:
        print(f'Warning: too much cpu!! Recommend {core_one_process * fileNum}')

    file = next(file_iter)    
    residul_core = coreNum

    while file != "finish0":
        # set opt file name 
        opt = get_opt_name(outdir,file) 

        # Available cores large than threshold
        if residul_core > core_one_process:
            p = multiprocessing.Process(target=calc_stastic_real, args=(file, core_one_process, tolearance, start_position, end_position, window_size, window_step, opt))
            p.start()
            process_info.append(p, core_one_process)
            process_info.add(1)
            residul_core -= core_one_process # updata residul core number
            file = next(file_iter)

        else:
            # Available cores large than 0
            if residul_core > 0:
                p = multiprocessing.Process(target=calc_stastic_real, args=(file, residul_core, tolearance, start_position, end_position, window_size, window_step, opt))
                p.start()
                process_info.append(p, residul_core)
                process_info.add(1)
                residul_core -= residul_core # updata residul core number
                file = next(file_iter)
            # Available core equal 0
            else: 
                while np.sum([p.is_alive() for p in process_info.process]) == process_info.run_number:
                    time.sleep(30)
                core_relase = process_info.update()
                residul_core += core_relase
    
    while not process_info.end():
        time.sleep(30)
    return 0

if __name__ == "__main__":
    nameSet = sys.argv[1]
    coreNum = int(sys.argv[2])
    tolearance = int(sys.argv[3])
    start_position = sys.argv[4]
    end_position = sys.argv[5]
    window_size = int(sys.argv[6])
    window_step = sys.argv[7]
    outdir = sys.argv[8]
    
    # check input is directory
    if os.path.isdir(nameSet):
        if not nameSet.endswith('/'):
            dirpath = nameSet + '/'
        else:
            dirpath = nameSet

        nameSet = [dirpath + name for name in os.listdir(dirpath)] 
        if len(nameSet) != np.sum([True for n in nameSet if n.endswith('.vcf.gz') or n.endswith('.vcf')]):
            print("Error:The files in the input folder must be .vcf or .vcf.gz files.")
            sys.exit(1)
    
    # input is multi file with ',' split 
    else:
        nameSet = nameSet.split(',')

    if not outdir.endswith('/'):
        outdir = f'{str(outdir)}/'

    if not os.path.exists(outdir):
        subprocess.call(f"mkdir {outdir}",shell=True)

    if len(nameSet) > 1:
        try:
            start_position == end_position == "None"
        except Exception as e:
            print("Error:The start and stop sites are not allowed \
                when multiple VCF files are passed into the program!!!. ")
    
    # feature computation 
    process_scheduling()
    # feature map generation
    for name in nameSet:
        get_featureMap(name,outdir)





