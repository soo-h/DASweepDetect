import sys
import subprocess
## 通过读取configure文件进行模拟
## step1.读取configure文件
## step2.判断是否符合模拟条件
## step3.调用discoal进行数据模拟

## step1.
##参数列表
# def convert_float(character):
#     try:
#         character = float(character)
#     except Exception as e:
#         print(e.args)
#         print(e)
#         print(repr(e))
#         print(f"Error:{character} should be float")
#         sys.exit()

def parameter_check(option,parameter):
    single = ['rep','hap','len','t','r','a','u','x','f','c','N']
    double = ['Pt','Pr','Pre','Pa','Pu','Px','Pf','Pc','d']
    _ = ' '.join(parameter)

    if option in single:
        if len(parameter) != 1:
            raise ValueError(f'invalid parameter {_}: {option} should have one parameter')

        # if sum(p.replace(".",'').isdigit() for p in parameter) != 1:
        #     raise ValueError(f'{_} should be composed of numbers!!!')
        return _

    if option in double:
        if len(parameter) != 2:
            raise ValueError(f'invalid parameter {_}: {option} should have two parameter')

        # if sum(p.replace(".",'').isdigit() for p in parameter) != 2:
        #     raise ValueError(f'{_} should be composed of numbers!!!')
        return _

    if option == 'en':
        if len(parameter) != 3:
            raise ValueError(f'invalid parameter {_}: {option} should have three parameter')

        # if sum(p.replace(".",'').isdigit() for p in parameter) != 3:
        #     raise ValueError(f'{_} should be composed of numbers!!!')
        return _

    if option == 'ws':
        if len(parameter) > 1:
            raise ValueError(f'invalid parameter {_}: {option} should have three parameter')
        if sum(p.replace(".",'').isdigit() for p in parameter) > 1:
            raise ValueError(f'{_} should be composed of numbers!!!')
        return _

    if option == 'Pxx':
        if _.count('-') != 2:
            raise ValueError(f'invalid parameter {_}: {option} should have two parameter of region \n Example 0.1-0.4 0.6-0.9')
        
        return [p.replace("-",' ') for p in _.split()] 


def option_check(option,parameter):
    option_list = ['rep','hap','len','Pt','t','Pr','Pre','r','Pa','a','Pu','u','Px','x','Pf','f','N','ws','c','Pc','en','d','Pxx']
    if option not in option_list:
        raise ValueError(f'invalid option: {option};.... to find all option')
    
    parameter = parameter_check(option,parameter)

    return option,parameter


configure_file = sys.argv[1]
out_file = sys.argv[2]

with open(configure_file) as f:
    configure_dict = {}
    essen_parameter = {}
    while line := f.readline():
        line = line.strip().split()
        option = line[0]
        parameter = line[1:]
        ## 检查选项和参数
        option,parameter = option_check(option,parameter)

        if option in ['hap','rep','len']:
            essen_parameter[option] = parameter
            continue

        if option == 'en' and option in configure_dict:
            configure_dict[f'{option}'] += f' -en {parameter}'
        ## 读取参数
        else:
            configure_dict[f'{option}'] = parameter

if 'Pxx' in configure_dict:
    rep1 = int(essen_parameter['rep']) // 2
    rep2 = int(essen_parameter['rep']) // 2 + 1

    configure_dict1 = {}
    configure_dict2 = {}
    for key in configure_dict:
        if key == 'Pxx':
            configure_dict1[key] = configure_dict[key][0]
            configure_dict2[key] = configure_dict[key][1]
        else:
            configure_dict1[key] = configure_dict[key]
            configure_dict2[key] = configure_dict[key]

    cmd1 = [
    'discoal',
    essen_parameter['hap'],
    str(rep1),
    essen_parameter['len'],
] + [f'-{key} {configure_dict1[key]}' for key in configure_dict] + ['>',f'{out_file}_1']

    cmd2 = [
    'discoal',
    essen_parameter['hap'],
    str(rep2),
    essen_parameter['len'],
] + [f'-{key} {configure_dict2[key]}' for key in configure_dict] + ['>',f'{out_file}_2']
    cmd1 = ' '.join(cmd1)
    cmd2 = ' '.join(cmd2)

    for cmd in [cmd1,cmd2]:
        subprocess.call(cmd,shell=True)
    
    cmd = f'cat {out_file}_1 {out_file}_2 > {out_file} && rm -f {out_file}_1 f{out_file}_2'
    subprocess.call(cmd,shell=True)
## 生成命令行
else:
    cmd = ['discoal',essen_parameter['hap'],essen_parameter['rep'],essen_parameter['len'],] + \
        [f'-{key} {configure_dict[key]}' for key in configure_dict] + ['>',out_file]

    cmd = ' '.join(cmd)
    ## 调用discoal进行模拟
    subprocess.call(cmd,shell=True)
