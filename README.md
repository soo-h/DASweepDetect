# DASD
Detection and classification selective sweep use domain adaptive model 


# 1.安装

```shell
git clone https://github.com/soo-h/DASD
```

由于未公开代码仓库，当前采用配置ssh key的方式下载

```shell
git clone git@github.com:soo-h/DASD.git
```



# 2.配置环境

## 2.1 python3.8安装和虚拟环境设置

###  python3.8安装

1.下载和解压

```shell
wget https://www.python.org/ftp/python/3.8.2/Python-3.8.2.tgz

tar -zxvf Python-3.8.2.tgz

cd Python-3.8.2
```

2. 安装

   ```shell
   ./configure
   ## 指定路径安装$PATH
   ./configure --prefix=$PATH
   
   make
   
   make install
   ```



**建议：创建虚拟环境**

```shell
python -m venv my_project_env  # 创建虚拟环境
source my_project_env/bin/activate  # 激活虚拟环境
```



## 2.2 环境配置

<1> python3 第三方库

```shell
pip3.8 install -r require.txt
```

<2> discoal软件安装

将编译后的discoal二进制包放入代码仓库，用户直接下载即可。若需重新编译，则

[kr-colab/discoal: discoal is a coalescent simulation program capable of simulating models with recombination, selective sweeps, and demographic changes including population splits, admixture events, and ancient samples (github.com)](https://github.com/kr-colab/discoal)

通过该链接下载后重新编译。





# 3.使用

## 3.1.数据模拟

数据模拟通过discoal软件完成

### 3.1.1.模拟数据配置文件说明

配置文件见DASD/simu_config 文件夹下，每个类别数据对应一个配置文件。需考虑的配置参数包含：

- rep：模拟次数（默认为2500，表示进行2500次模拟，生成2500组选择信号模拟数据）
- hap：染色体条数（默认为100）
- len：染色体片段长度（默认为100kbp，discoal软件最大长度为220kbp，若需更长的片段，需重新编译discoal软件。见2.2 <2>）
- Pt：突变率取值范围，由上限和下限两个数值组成，需用户提供。
- Pr：重组率取值范围，由上限和下限两个数值组成，需用户提供。
- Pu：选择结束时间和抽样时间的间隔（默认为0.0005982817348574893 0）
- Pa：选择强度取值范围，由上限和下限两个数值组成，需用户提供。
- Px：受选择位点发生区域（默认为0.475 0.525）
- Pxx：受选择位点不连续，使用该参数，默认为（）
- en：群体历史参数，需用户提供。格式为



### 3.1.2.模拟命令

使用**simu** 功能完成

配置文件应命名为"\<name\>\_"configure.txt，输出的模拟数据为 "\<name\>\_simulation"。

<1> 以文件夹为输入

使用 **-i** 参数传入文件夹的路径，传入的文件夹内应仅包含配置文件；

使用 **-o** 参数设置输出文件夹路径



**demo:**

```shell
python3.8 DASD.py simu -i simu_config/ -o simu_data
```

<2> 以配置文件为输入

使用 **-i** 参数传入配置文件；

使用 **-o** 参数设置输出文件夹路径



**demo:**

```shell
python3.8 DASD.py simu -i simu_config/chSel_configure.txt -o simu_data
```



## 3.2.模拟数据特征工程

使用**calc_domain**功能完成

参数：

- **-i** 或 **--input**：模拟数据文件所在文件夹，或单个或多个模拟数据文件（以','为分割符）
- **--filter** : 设置剔除样本的标准，默认为250，即剔除SNP少于250的样本
- **--core** : 设置使用CPU数，建议使用8的倍数，且不应超过n*8，n为传入的文件数(或文件夹内的文件数)，默认为16
- **-o** 或 **--out**：输出文件夹



**demo:**

```shell
python3.8 DASD.py calc_domain -i simu_data --filter 250 --core 16 -o simu_feature
```



## 3.3. 真实数据特征工程

使用**calc_target** 功能完成

参数：

- **-i** 或 **--input**：模拟数据文件所在文件夹，或单个或多个模拟数据文件（以','为分割符）
- **--filter** : 设置剔除样本的标准，默认为250，即剔除SNP少于250的样本
- **--core** : 设置使用CPU数，建议使用8的倍数，且不应超过n*8，n为传入的文件数(或文件夹内的文件数)，默认为16
- **-o** 或 **--out**：输出文件夹



**demo:**

```shell
python3.8 DASD.py calc_domain -i real_data --filter 250 --core 16 -o real_feature
```



## 3.4. 数据标注

使用**data_annotation**完成

参数：

- **-i** 或 **--input**：模拟数据文件所在文件夹，或单个或多个模拟数据文件（以','为分割符）
- **--config** : 配置文件，包含标注信息
- **-o** 或 **--out**：输出文件夹

```shell
python3.8 DASD.py data_annotation -i simu_feature --config label_configure.txt -o trainSet
```



**配置文件说明：**

配置文件见DASD/label_configure.txt



## 3.5.模型训练

使用**train**完成

参数：

- **--train-data** : 训练集数据
- **--train-label** : 训练集标签
- **--valid-data** : 验证集数据
- **--valid-label**: 验证集标签
- **--test-data** ：测试集数据
- **--test-label** ： 测试集标签
- **-t** 或 **--target** ： 目标域数据集
- **-o** 或 **--out** ： 模型输出文件夹



**demo:**

```shell
python3.8 DASD.py train --train-data trainSet/trainSet.npy --train-label trainSet/trainSet_label.npy --valid-data trainSet/validSet.npy --valid-label trainSet/validSet_label.npy --test-data trainSet/testSet.npy --test-label trainSet/testSet_label.npy -t real_feature/ -o ../Ensemble_CEU
```



## 3.6.预测





# 4.输出结果说明
