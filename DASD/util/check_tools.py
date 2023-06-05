import os

def get_input_file(path):
    """
    input : path
    reurn : 
            if path is directory : list ,consist of file name
            if path is file which split of , : list, consist of file name
    
    """

    if os.path.isdir(path):
        if not path.endswith('/'):
            path = path + '/'
    
        nameSet = [path + name for name in os.listdir(path)]
    
    else:
        nameSet = path.split(',')
    return nameSet

def check_label_config(lab_dict):
    # 检查是否为整数
    for key in lab_dict:
        try:
            lab_dict[key] = int(lab_dict[key])
        except ValueError as e:
            print(e)
            print("Error: label must be integers and greater than or equal to 0 !")

    # 检查label 和category 一一对应
    if len(lab_dict) != len(set(lab_dict.values())):
        raise ValueError('The category must correspond to the label one by one.\n' + \
                         '\tCheck whether the label is repeated in different categories!')
    # 检查label是否连续
    label = list(lab_dict.values())
    if max(label) - min(label) != len(label) - 1:
        raise ValueError('Label must be consecutive !')

    return 0
