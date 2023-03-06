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
