import numpy as np
import gzip


def read_vcf(file,start_position=None,end_position=None):
    if file.endswith('.gz'):
        f = gzip.open(file, 'rt')
    else:
        f = open(file, 'rt')

    con = True
    head = []
    while con:
        line = f.readline()
        if line.startswith('##'):
            li = line.strip().split()
            head.append(li)
        if line.startswith('#CHROM'):
            con = False

    
    mat_hap = []
    pos_list = []
    for line in f:
        line = line.strip().split()
        pos = float(line[1])
        if start_position and pos < start_position:
            continue
        if end_position and pos > end_position:
            break
        if len(line[3]) != 1 or len(line[4]) != 1:
            continue
        pos_list.append(pos)
        snp = line[9:]
        snp = [i.split('|')[j] for i in snp for j in range(2)]
        mat_hap.append(snp)

    f.close()
    return mat_hap, pos_list




def convert_one_zero(snpMatrix,filtpos):
    filtpos = np.asarray(filtpos)
    snpMatrix_ = np.empty(shape=(len(snpMatrix),len(snpMatrix[0])))
    snpMatrix_[:] = snpMatrix

    snpMatrix_ = np.array(snpMatrix_,dtype='i4')
    snpMatrix_[(snpMatrix_ != 0)&(snpMatrix_ != 1)] = 1
    return snpMatrix_,filtpos

def filt_nobiallel(mat_hap,pos_list):
    #delid = []
    filtpos = []
    snpMatrix = []
    for i in range(len(mat_hap)):
        if len(set(mat_hap[i])) == 2:
            filtpos.append(pos_list[i])
            snpMatrix.append(mat_hap[i])

    snpMatrix,filtpos = convert_one_zero(snpMatrix,filtpos)

    return snpMatrix,filtpos


def vcf_to_matrix_pos(file,start_position=None,end_position=None):

    mat_hap,pos_list = read_vcf(file)
    snpMatrix,filtpos = filt_nobiallel(mat_hap,pos_list)
    return snpMatrix,filtpos
