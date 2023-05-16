import sys
import subprocess
import math
import copy
import os
import multiprocessing

from util.check_tools import get_input_file


configure_file = sys.argv[1]
out_dir = sys.argv[2]
discoal = sys.argv[3]


if not out_dir.endswith('/'):
    out_dir += '/'

if not os.path.exists(out_dir):
    subprocess.call(f'mkdir -p {out_dir}', shell=True)

configure_file = get_input_file(configure_file)



class Simulator:
    def __init__(self):
        self.option_list = ['rep', 'hap', 'len', 'Pt', 't', 'Pr', 'Pre', 'r', 'Pa', 'a', 'Pu', 'u', 'Px', 'x', 'Pf',
                            'f',
                            'N', 'ws', 'c', 'Pc', 'en', 'd', 'Pxx']
        self.single = ['rep', 'hap', 'len', 't', 'r', 'a', 'u', 'x', 'f', 'c', 'N']
        self.double = ['Pt', 'Pr', 'Pre', 'Pa', 'Pu', 'Px', 'Pf', 'Pc', 'd']
        self.configure_dict = {}
        self.essen_parameter = {}

    def parameter_read(self, option, parameter):
        _ = ' '.join(parameter)
        if option in self.single:
            if len(parameter) != 1:
                raise ValueError(f'invalid parameter {_}: {option} should have one parameter')

            return _

        if option in self.double:
            if len(parameter) != 2:
                raise ValueError(f'invalid parameter {_}: {option} should have two parameter')

            return _

        if option == 'en':
            if len(parameter) != 3:
                raise ValueError(f'invalid parameter {_}: {option} should have three parameter')

            return _

        if option == 'ws':
            if len(parameter) > 1:
                raise ValueError(f'invalid parameter {_}: {option} should less one parameter')
            return _

        if option == 'Pxx':
            if _.count('-') != 2:
                raise ValueError(
                    f'invalid parameter {_}: {option} should have two parameter of region \n Example 0.1-0.4 0.6-0.9'
                )

            return [p.replace("-", ' ') for p in _.split()]

    def option_check(self, option):
        if option not in self.option_list:
            raise ValueError(f'invalid option: {option};.... to find all option')
        return 0

    def save_parameter(self, option, parameter):
        self.option_check(option)
        parameter = self.parameter_read(option, parameter)
        if option in ['hap', 'rep', 'len']:
            self.essen_parameter[option] = parameter

        elif option == 'en' and option in self.configure_dict:
            self.configure_dict[option] += f' -en {parameter}'

        else:
            self.configure_dict[option] = parameter

    def cmd_gene(self, opt,discoal=discoal):
        if 'Pxx' in self.configure_dict:
            rep1 = int(self.essen_parameter['rep']) // 2
            rep2 = math.ceil(int(self.essen_parameter['rep']) // 2)

            configure_dict1 = copy.deepcopy(self.configure_dict)
            configure_dict2 = copy.deepcopy(self.configure_dict)

            configure_dict1['Pxx'] = self.configure_dict['Pxx'][0]
            configure_dict2['Pxx'] = self.configure_dict['Pxx'][1]

            cmd1 = [
                       discoal,
                       self.essen_parameter['hap'],
                       str(rep1),
                       self.essen_parameter['len'],
                   ] + [f'-{key} {configure_dict1[key]}' for key in self.configure_dict] + ['>', f'{opt}_1']

            cmd2 = [
                       discoal,
                       self.essen_parameter['hap'],
                       str(rep2),
                       self.essen_parameter['len'],
                   ] + [f'-{key} {configure_dict2[key]}' for key in self.configure_dict] + ['>', f'{opt}_2']
            cmd1 = ' '.join(cmd1)
            cmd2 = ' '.join(cmd2)

            return [cmd1, cmd2]

        else:
            cmd = [discoal, self.essen_parameter['hap'], self.essen_parameter['rep'], self.essen_parameter['len'], ]\
                + [f'-{key} {self.configure_dict[key]}' for key in self.configure_dict] + ['>', opt]

            cmd = ' '.join(cmd)

            return [cmd]


def get_cmd_list(file):
    with open(file) as f:
        simulator = Simulator()
        while line := f.readline():
            line = line.strip().split()
            option = line[0]
            parameter = line[1:]
            simulator.save_parameter(option, parameter)
    return simulator


def run_simulation_by_discoal(cmd_list,out_file):
    move_cmd = []

    for cmd in cmd_list:
        # 模拟
        subprocess.call(cmd, shell=True)
        move_cmd.append(cmd.split('>')[-1])

    if len(move_cmd) > 1:
        # 合并 移除
        cmd_cat = 'cat ' + ' '.join(move_cmd) + f' > {out_file}'
        subprocess.call(cmd_cat, shell=True)
        cmd_remove = f'rm -f ' + ' '.join(move_cmd)
        subprocess.call(cmd_remove, shell=True)

    return 0




# 每个文件使用一个核
for configure in configure_file:
    _ = configure.split('/')[-1]
    suffix = _.split('_configure.txt')[0]
    out_file = out_dir + suffix + '_simulation'
    simulator = get_cmd_list(configure)

    cmd_list = simulator.cmd_gene(out_file)

    p = multiprocessing.Process(target=run_simulation_by_discoal, args=[cmd_list,out_file])
    p.start()
