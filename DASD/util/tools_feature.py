import numpy as np
import sys


def namesort(nameSet):
    
    sort_name = []
    for sta in ['HAFStastic','safe','kappa','phi','dihhStastic',\
        'ihsStastic','nslStastic','sfsStastic','allelFrebaseStastic','hapFrebaseStastic']:
        for name in nameSet:
            if name.endswith(sta):
                nameSet.remove(name)
                sort_name.append(name)
    
    return sort_name 
            
    
def readstar_step(name):
    if ('ihs' in name) | ('nsl' in name)  | ('dihh' in name):
        star = 0 
        step = 1
        
    elif ('HAF' in name) | ('safe' in name) | ('kappa' in name) | ('phi' in name) | ('allel' in name):
        star =0 
        step = 5
        
    elif ('hapFre' in name) | ('sfs' in name):
        star = 0
        step = 6
        
    else:
        sys.exit('Error')
    
    return star,step



def readstastic(name):
    
    star,step = readstar_step(name)
    t = np.loadtxt(name)
    dim1 = int(t.shape[0] / step)
    t_sta = np.zeros(shape=(dim1,step-star,200))
    for epoch in range(star,step):
        t_sta[:,epoch] = t[epoch::step]
    return t_sta

def loadstastic(nameSet):

    nameSet = namesort(nameSet)
    print(nameSet)

    return np.concatenate([readstastic(name) for name in nameSet],axis=1)