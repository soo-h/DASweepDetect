import sys
import numpy as np


def ms_read(file):
    # 输出单倍型矩阵shape：(hap,varience)
    f = open(file,'r')
    headerIn = []
    segsiteIn = []
    header = f.readline()
    headerIn.append(header)
    program, numSamples, numSims = header.strip().split()[:3]
    numSamples, numSims = int(numSamples), int(numSims)

    hapArraysIn = []
    positionArrays = []
    # advance to first simulation
    line = f.readline()
    while line.strip() != "//":
        line = f.readline()
    while line:
        if line.strip() != "//":
            sys.exit(
                "Malformed ms-style output file: read '%s' instead of '//'. \n" % (line.strip()))  # NOQA
        segsitesBlah, segsites = f.readline().strip().split()
        segsites = int(segsites)
        segsiteIn.append(segsites)

        if segsitesBlah != "segsites:":
            sys.exit("Malformed ms-style output file. \n")
        if segsites == 0:
            positions = []
            hapArrayIn = []
            for i in range(numSamples):
                hapArrayIn.append([])
        else:
            positionsLine = f.readline().strip().split()
            if not positionsLine[0] == "positions:":
                sys.exit("Malformed ms-style output file. \n")
            positions = [float(x) for x in positionsLine[1:]]

            samples = []
            for i in range(numSamples):
                sampleLine = f.readline().strip()
                if len(sampleLine) != segsites:
                    sys.exit("Malformed ms-style output file %s segsites but %s columns in line: %s; line %s of %s samples \n" %  # NOQA
                                (segsites, len(sampleLine), sampleLine, i, numSamples)) # NOQA
                #根据nsample和segsite构建np.array用于存储数据，可能会提升速度
                samples.append([int(i) for i in sampleLine])
            if len(samples) != numSamples:
                raise Exception
        hapArraysIn.append(samples)
        positionArrays.append(positions)
        line = f.readline()
        # advance to the next non-empty line or EOF
        while line and line.strip() == "":
            line = f.readline()
        if line[:3] == "dis":
            header = line
            headerIn.append(header)
            program, numSamples, numSims = header.strip().split()[:3]
            numSamples, numSims = int(numSamples), int(numSims)
        while line and line.strip() != "//":
            line = f.readline()
         #sys.stderr.write("finished rep %d\n" %(len(hapArraysIn)))
    #if len(hapArraysIn) != numSims:
        #sys.exit("Malformed ms-style output file: %s of %s sims processed. \n" % # NOQA
                    #(len(hapArraysIn), numSims))

    f.close()
    return headerIn,segsiteIn,hapArraysIn, positionArrays





def ms_read_pipline(file,cutoff):  # sourcery skip: raise-specific-error
    # 输出单倍型矩阵shape：(hap,varience)
    f = open(file,'r')
    #filt_count = 0

    headerIn = []
    segsiteIn = []
    header = f.readline()
    headerIn.append(header)
    _, numSamples, numSims = header.strip().split()[:3]
    numSamples, numSims = int(numSamples), int(numSims)

    # advance to first simulation
    line = f.readline()
    while line.strip() != "//":
        line = f.readline()
    while line:
        if line.strip() != "//":
            sys.exit(
                "Malformed ms-style output file: read '%s' instead of '//'. \n" % (line.strip()))  # NOQA
        segsitesBlah, segsites = f.readline().strip().split()
        segsites = int(segsites)
        segsiteIn.append(segsites)

        if segsitesBlah != "segsites:":
            sys.exit("Malformed ms-style output file. \n")

        if segsites == 0:
            positions = []
            hapArrayIn = []
            for i in range(numSamples):
                hapArrayIn.append([])
        else:
            positionsLine = f.readline().strip().split()
            if not positionsLine[0] == "positions:":
                sys.exit("Malformed ms-style output file. \n")
            positions = np.asarray([float(x) for x in positionsLine[1:]])

            samples = np.empty(shape=(numSamples,len(positions)))
            for i in range(numSamples):
                sampleLine = f.readline().strip()
                if len(sampleLine) != segsites:
                    sys.exit("Malformed ms-style output file %s segsites but %s columns in line: %s; line %s of %s samples \n" %  # NOQA
                                (segsites, len(sampleLine), sampleLine, i, numSamples)) # NOQA
                #根据nsample和segsite构建np.array用于存储数据，可能会提升速度
                samples[i] =  [int(i) for i in sampleLine]
            samples = np.asarray(samples,dtype=int)
            if samples.shape[0] != numSamples:
                raise Exception
        
        if segsites < cutoff:
            #filt_count += 1
            pass
        else:
            yield (samples,positions)
        line = f.readline()
        # advance to the next non-empty line or EOF
        while line and line.strip() == "":
            line = f.readline()
        if line[:3] == "dis":
            header = line
            headerIn.append(header)
            program, numSamples, numSims = header.strip().split()[:3]
            numSamples, numSims = int(numSamples), int(numSims)
        while line and line.strip() != "//":
            line = f.readline()

    f.close()


def drow_grid(position,gridNum=200,snpNum=50,edge=False):    
    # 检查输入数据
    if not isinstance(position,np.ndarray):
        position = np.asarray(position,dtype='float')
        print('Warmning: position is not array_like,check input data!!!')

        
    #centeral snp 在该位置附近抽取
    step = (position[-1]-position[0]) / (gridNum +1 )
    snpNumside = snpNum // 2
    #star = step / 2
    star = position[0] + step
    
    for _ in range(gridNum+1):
        # centeral snp左侧无snp
        if np.sum([position<star]) == 0 :
            star += step
            continue
        # 获取centeral snp 的index
        index = np.argmax(position[position<star])
        
        star += step
        right = index + snpNumside
        left = index - snpNumside
        if right > len(position):
            if edge:
                right = len(position) - 1
               
                continue
            else:
                return 
        if left < 0:
            if edge:  
                left = 0 
                
            else:
                
                continue
        yield((left,right))

def dropgrid_statComput(static,snpMatrix,position,gridNum=200,snpNum=50,edge=True):
    """
    static : function
            用于计算的统计量
    gridNum: int
            期望的单倍型窗口数
    snpNum: int
            每个窗口需包含的snp数
    edge:   bool
            窗口snp不足时是否进行计算
    """
    if not isinstance(snpMatrix,np.ndarray):
        snpMatrix = np.asarray(snpMatrix,dtype='i4')
        print('Warmning: snpMatrix is not array_like,check input data!!!')
        
    
    windows = drow_grid(position,gridNum,snpNum,edge=edge)
    # setup output
    out_value,out_pos = [],[]
 
    for i,j in windows:
        # 统计量需要1个参数
        if static.__code__.co_argcount == 1:
            out_value.append(static(snpMatrix[:,i:j]))
        # 需两个参数
        elif static.__code__.co_argcount == 2:
            out_value.append(static(position[i:j],snpMatrix[:,i:j]))
        
        out_pos.append(np.mean(position[i:j]))
    
    out_value,out_pos = np.asarray(out_value),np.asarray(out_pos)
    
    
    return out_value,out_pos

def Phy_Win1D(pos,value,cutpos):
    """
    pos : array_like 由position构成
    value : array_like 由统计量值构成
    cutpos : int 根据physical distance生成的值的个数
    """

    valueBin = np.zeros(len(cutpos),dtype=float)
    posBin = np.zeros(len(cutpos),dtype=float)
    
    j = 0
    for index in range(len(cutpos)):
        i = cutpos[index]
        loc = (pos>=j) & (pos<i)
        if np.sum(loc):
            posBin[index] = np.mean(pos[loc])
            valueBin[index] = np.mean(value[loc])
        j = i
    
    return posBin,valueBin

def Phy_Win2D(pos,value,cutpos):
    """
    pos : array_like 由position构成
    value : array_like shape=(grid,nsta) 行为grid数,每列为一个统计量
    cutpos : int 根据physical distance生成的值的个数
    """
    nvalue = value.shape[1]
    valueBin = np.zeros(shape=(nvalue,len(cutpos)),dtype=float)
    
    posBin = np.zeros(len(cutpos),dtype=float)

    j = 0
    for index in range(len(cutpos)):
        i = cutpos[index]
        loc = (pos>=j) & (pos<i)
        if np.sum(loc):
            posBin[index] = np.mean(pos[loc])
            valueBin[:,index] = np.mean(value[loc],axis=0)
        j = i
    return posBin,valueBin

def Phy_Win(pos,value,region=200):
    """
    用于模拟数据的physical windows,真实数据与之不同
    因为真实数据需对绝对位置信息有需求,而模拟数据默认位置位于0-1间
    """
    if max(pos) > 1:
        pos = pos / 100000
    pos = np.array(pos)
    value = np.array(value)
    
    region = int(region)
    right = region + 1
    #生成200个bin
    cutpos = [i/region for i in range(1,right)]
    if value.ndim == 2:
        posBin,valueBin = Phy_Win2D(pos,value,cutpos)
    
    #将数据放入bin内
    else:
        posBin,valueBin = Phy_Win1D(pos,value,cutpos)

    return posBin,valueBin



############下方函数未进行二轮整合
####################用于EHH方法的daf windows############
def daf_Win(daf,value,pos,region=200):
    """
    uncheck : 是否同时适用于模拟数据和真实数据
    """
    daf_Pw = []
    fre_d_Wp = []
    pos_Wp = []
    
    daf = np.array(daf)
    value = np.array(value)
    pos = np.array(pos)
    
    region = int(region)
    right = region + 1
    #生成200个bin
    cutdaf = [i/region for i in range(1,right)]
    
    #将数据放入bin内
    j=0
    for i in cutdaf:
        d = daf[daf>=j]
        v = value[daf>=j] 
        p = pos[daf>=j] 
        
        daf_Pw.append(d[d<i])
        fre_d_Wp.append(v[d<i])
        pos_Wp.append(p[d<i])
        j=i
    return daf_Pw,fre_d_Wp,pos_Wp
###################### 用于real data 的窗口函数
def position_windows(pos, size, start, stop, step):

    last = False

    # determine start and stop positions
    if start is None:
        start = int(pos[0])
    if stop is None:
        stop = int(pos[-1])
    if step is None:
        # non-overlapping
        step = size
    print(start,stop,step)
    windows = []
    for window_start in range(start, stop, step):

        # determine window stop
        window_stop = window_start + size
        if window_stop >= stop:
            # last window
            window_stop = stop
            last = True
        else:
            window_stop -= 1

        windows.append([window_start, window_stop])

        if last:
            break

    return np.asarray(windows)


def window_loc(pos,windows):
    windows = np.asarray(windows)
    start_locs = np.searchsorted(pos, windows[:, 0])
    stop_locs = np.searchsorted(pos, windows[:, 1], side='left')
    return np.column_stack((start_locs, stop_locs))

def window_locations(pos,windows):
    windows = np.asarray(windows)
    start_locs = np.searchsorted(pos, windows[:, 0])
    stop_locs = np.searchsorted(pos, windows[:, 1], side='left')
    return np.column_stack((pos[start_locs], pos[stop_locs]))

def vector_loc(pos,region=200):

    #返回基于位置信息划分的200个bin的坐标
    start = int(pos[0])
    end = int(pos[-1])
    step = (end -start) / region

    windows = []
    for window_start in np.arange(start, end, step):
        window_stop = window_start + step
        if window_stop >= end:
            # last window
            windows.append([window_start, window_stop-1])
            break
        else:
            window_stop -= 1

        windows.append([window_start, window_stop])

    if len(windows) > 200:
        windows = windows[:200]
    return window_locations(pos,windows)

def Phy_Win1D_real(pos,value,cutpos):
    valueBin = np.zeros(len(cutpos),dtype=float)
    posBin = np.zeros(len(cutpos),dtype=float)

    for index in range(len(cutpos)):
        left,right = cutpos[index]
        loc = (pos>=left) & (pos<right)
        if np.sum(loc):
            posBin[index] = np.mean(pos[loc])
            valueBin[index] = np.mean(value[loc])

    return posBin,valueBin

def Phy_Win2D_real(pos,value,cutpos):
    #假设pos、value已是数组
    nvalue = value.shape[1]
    valueBin = np.zeros(shape=(nvalue,len(cutpos)),dtype=float)
    posBin = np.zeros(len(cutpos),dtype=float)

    for index in range(len(cutpos)):
        left,right = cutpos[index]
        loc = (pos>=left) & (pos<right)
        if np.sum(loc):
            posBin[index] = np.mean(pos[loc])
            valueBin[:,index] = np.mean(value[loc],axis=0)
    return posBin,valueBin

def Phy_Win_real(pos,value,locs):

    #生成200个bin
    if value.ndim == 2:
        return Phy_Win2D_real(pos,value,locs)

    #将数据放入bin内
    else:
        return Phy_Win1D_real(pos,value,locs)