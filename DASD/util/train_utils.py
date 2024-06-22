import os

def parse_model_name(model_name):
    """
    Parse the model name to extract the directory path and the prefix of the model name.
    
    Args:
        model_name (str): The complete model name which may include a directory path.

    Returns:
        tuple: A tuple containing the model directory path and the model name prefix.
    """
    model_dir_path, model_name_prefix = os.path.split(model_name)
    if not model_dir_path:
        model_dir_path = './'
    else:
        model_dir_path += '/'

    return model_dir_path, model_name_prefix

def get_target_data_paths(target_path):
    """
    Get paths of target data files.
    
    Args:
        target_data (str): Directory or comma-separated list of file paths.
        
    Returns:
        list: List of target data file paths.
    """
    if os.path.isdir(target_path):
        target_data_paths = [os.path.join(target_path, name) for name in os.listdir(target_path) if name.endswith("npy")]
    else:
        target_data_paths = target_path.split(',')
    
    return target_data_paths