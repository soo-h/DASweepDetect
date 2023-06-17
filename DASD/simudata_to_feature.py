import sys
import time
import os
import warnings
import copy
import subprocess
import multiprocessing

import setproctitle
setproctitle.setproctitle("DASDC")
import numpy as np
from script_simu_fev.Data_To_Feature_pipline import write_haf, write_sfs, write_hapFre, write_allelFre\
    , write_safe, write_ihs, write_nsl, write_dihh
from util.window_tools import ms_read_pipline
from util.tools_feature import loadstastic
from util.check_tools import get_input_file

warnings.filterwarnings("ignore")

nameSet = sys.argv[1]

coreNum = int(sys.argv[2])
cutoff = int(sys.argv[3])

outdir = sys.argv[4]

nameSet = get_input_file(nameSet)
print(nameSet)

if outdir == '.':
    outdir = os.getcwd()
if not outdir.endswith('/'):
    outdir = f'{str(outdir)}/'

# 模型训练所需最小样本数---待定
min_sample = 3000


def iter_file(fileSet):
    file_iter = iter(fileSet)
    while True:
        try:
            yield (next(file_iter))
        except Exception:
            break
    yield "finish0"


def para_run(process_query, coreNum):
    """
    进程管理,基于CPU核心数和要执行进程数，对资源进行分配。
    :param process_query: 生成器；包含要执行的进程对象（multiprocess.Process）
    :param coreNum: 被分配给任务的核心数
    :return: 任务全部完成时返回
    """
    process_running = []

    for _ in range(coreNum):
        p = next(process_query)
        process_running.append(p)
        p.start()

    while True:
        fin = False
        time.sleep(30)
        # 入队
        while sum(p.is_alive() for p in process_running) < coreNum:
            # 中止结束的进程
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

    # 等待任务子进程结束
    while sum(p.is_alive() for p in process_running) != 0:
        time.sleep(30)
    return 0


def calc_stastic_simu(file, core_num, cutoff, opt):
    """
    未判断用户是否有足够的cpu进行并行
    """
    name = file.split('/')[-1]
    opt = opt + name

    data_generator = ms_read_pipline(file, cutoff)

    haf_ = multiprocessing.Process(target=write_haf, args=(data_generator, opt))
    sfs_ = multiprocessing.Process(target=write_sfs, args=(data_generator, opt))
    hap_fre_ = multiprocessing.Process(target=write_hapFre, args=(data_generator, opt))
    alle_fre_ = multiprocessing.Process(target=write_allelFre, args=(data_generator, opt))
    safe_ = multiprocessing.Process(target=write_safe, args=(data_generator, opt))
    process_query = iter([haf_, safe_, sfs_, hap_fre_, alle_fre_])

    _ = para_run(process_query, core_num)

    return 0


def calc_ehh_base(name_list, core_num, cutoff, outdir):
    
    process_number = 3
    core_number_every_process = core_num // process_number
    residue_core = core_num % process_number
    
    # 为父进程和子进程分配资源
    if core_number_every_process > 0:
        core_list = [core_number_every_process if i != process_number-1 \
                         else core_number_every_process + residue_core \
                     for i in range(process_number) ]
        core_numer_p_process = 3
    else:
        core_list = [1,1,1]
        core_numer_p_process = core_num
    
    
    ihs = multiprocessing.Process(target=write_ihs, args=(name_list, cutoff, outdir, core_list[0]))
    nsl = multiprocessing.Process(target=write_nsl, args=(name_list, cutoff, outdir, core_list[1]))
    dihh = multiprocessing.Process(target=write_dihh, args=(name_list, cutoff, outdir, core_list[2]))

    process_query = iter([ihs, nsl, dihh])

    # 管理父进程(统计量)
    _ = para_run(process_query, core_numer_p_process)

    return 0

def get_featureMap(nameSet, outdir):
    # remain = True
    for file in nameSet:
        name = file.split('/')[-1]
        opt = outdir + name
        # 整理生成特征图
        featureNameSet = [outdir + caluc_name for caluc_name in os.listdir(outdir) if caluc_name.startswith(name)]
        featureMap = loadstastic(copy.deepcopy(featureNameSet))

        # if not remain
        # 删除中间文件
        cmd = 'rm -f ' + ' '.join(featureNameSet)
        print(cmd)
        subprocess.call(cmd, shell=True)
        # 保存特征图
        np.save(f'{opt}_featureMap', featureMap)
    return 0


class process_saver():
    def __init__(self):
        self.process = []
        self.core = []
        self.run_number = 0

    def append(self,process,core_num):
        self.process.append(process)
        self.core.append(core_num)

    def add(self,count):
        self.run_number += count

    def reduce(self,count):
        self.run_number -= count

    def update(self):
        # 记录释放出的核数
        release_core = 0
        new_process = []
        new_core = []
        for p, c in zip(self.process, self.core):
            if not p.is_alive():
                p.terminate()
                release_core += c
            else:
                new_process.append(p)
                new_core.append(c)

        self.process = new_process
        self.core = new_core

        return release_core

    def end(self):
        if np.sum([p.is_alive() for p in self.process]) != 0:
            return False
        else:
            return True


def process_scheduling():

    fileNum = len(nameSet)
    corenumber_need_by_one_file = 8
    max_core_number = corenumber_need_by_one_file * fileNum
    ehh_core_number = 3 * fileNum
    process_info = process_saver()
    file_iter = iter_file(nameSet)

    if coreNum > max_core_number:
        print(f"Warning: too much cpu!! Recommend {corenumber_need_by_one_file * fileNum}")

    # 先ehh再其它统计量
    if coreNum > ehh_core_number:
        residul_core = coreNum - ehh_core_number
        ehh = multiprocessing.Process(target=calc_ehh_base, args=(nameSet, ehh_core_number, cutoff, outdir))
        ehh.start()
        process_info.append(ehh,ehh_core_number)
        process_info.add(1)

        file = next(file_iter)
        while file != "finish0":
            if residul_core > 5:
                residul_core -= 5
                p = multiprocessing.Process(target=calc_stastic_simu, args=(file, 5, cutoff, outdir))
                process_info.append(p,5)
                p.start()
                process_info.add(1)
                file = next(file_iter)
            else:
                if residul_core > 0:
                    p = multiprocessing.Process(target=calc_stastic_simu, args=(file, residul_core, cutoff, outdir))
                    process_info.append(p,residul_core)
                    p.start()
                    residul_core = 0
                    process_info.add(1)
                    file = next(file_iter)
                else:
                    while np.sum([p.is_alive() for p in process_info.process]) == process_info.run_number:
                        time.sleep(30)
                    core_relase = process_info.update()
                    residul_core += core_relase

    # ehh执行完毕后执行其它统计量
    else:
        residul_core = 0
        ehh = multiprocessing.Process(target=calc_ehh_base, args=(nameSet, coreNum, cutoff, outdir))
        ehh.start()
        process_info.append(ehh,coreNum)
        process_info.add(1)

        file = next(file_iter)
        while file != "finish0":
            if residul_core > 5:
                residul_core -= 5
                p = multiprocessing.Process(target=calc_stastic_simu, args=(file, 5, cutoff, outdir))
                process_info.append(p,5)
                process_info.add(1)
                file = next(file_iter)
            else:
                if residul_core > 0:
                    p = multiprocessing.Process(target=calc_stastic_simu, args=(file, residul_core, cutoff, outdir))
                    process_info.append(p,residul_core)
                    residul_core = 0
                    process_info.add(1)
                    file = next(file_iter)
                else:
                    while np.sum([p.is_alive() for p in process_info.process]) == process_info.run_number:
                        time.sleep(30)
                    core_relase = process_info.update()
                    residul_core += core_relase

    while not process_info.end():
        time.sleep(30)
    return 0






if __name__ == '__main__':
    process_scheduling()
    get_featureMap(nameSet, outdir)
