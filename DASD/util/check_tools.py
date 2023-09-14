import os

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
    # check labels are int
    for key in lab_dict:
        try:
            lab_dict[key] = int(lab_dict[key])
        except ValueError as e:
            print(e)
            print("Error: label must be integers and greater than or equal to 0 !")

    # check labels and categories 
    if len(lab_dict) != len(set(lab_dict.values())):
        raise ValueError('The category must correspond to the label one by one.\n' + \
                         '\tCheck whether the label is repeated in different categories!')
    # check labels are continuous
    label = list(lab_dict.values())
    if max(label) - min(label) != len(label) - 1:
        raise ValueError('Label must be consecutive !')

    return 0
