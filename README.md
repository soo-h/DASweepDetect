

# 1.**Introduction**

**DASDC** 是一个基于深度学习（域对抗网络）用于选择信号识别并分类的软件，其工作示意图如下：

![image](https://github.com/soo-h/DASweepDetect/assets/74720083/1f471fde-3011-491f-a39b-69a04c832c96)
 <p align="center"><b>（DASDC工作示意图）</b></p>       



软件以**单群体vcf文件**和**该群体的群体遗传学参数、群体历史为输入**，通过六个步骤，完成选择信号的识别和分类。



如果您发现软件有任何错误或问题，请联系   

如果您使用此软件，请引用

# 2.**Installation**

```shell
git clone https://github.com/soo-h/DASweepDetect
```

## 2.1 python3.8 安装

软件目前需使用python 3.8版本及以上版本运行，install python on the command line enter:

```shell
wget https://www.python.org/ftp/python/3.8.6/Python-3.8.6.tgz
tar -zxvf Python-3.8.6.tgz
cd Python-3.8.6

./configure --prefix=$PATH

make
make install
```

$PATH是python安装的路径



## 2.2 创建虚拟环境（非必须）

**建议：创建虚拟环境**


   ```shell
python -m venv my_project_env  # 创建虚拟环境
source my_project_env/bin/activate  # 激活虚拟环境
   ```

命令1为 创建虚拟环境，命令2为激活所创建的虚拟环境。

## 2.3 依赖包安装

使用以下命令完成软件依赖的第三方库的安装

```shell
pip3.8 install -r require.txt
```



# 3.使用

- step1. 数据模拟（详见3.1）
- step2. 模拟数据特征工程（详见3.2）
- step3. 真实基因组数据特征工程（详见3.3）
- step4. 标注（详见3.4）
- step5. 模型训练（详见3.5）
- step6. 预测（详见3.6）



## 3.1.数据模拟

**Note：**数据模拟通过**discoal**软件完成，我们将编译后的**discoal**二进制包放入代码仓库。若需重新编译，通过下方链接下载后重新编译：

https://github.com/kr-colab/discoal



Citations

- Kern AD and Schrider DR 2016. https://doi.org/10.1093/bioinformatics/btw556



### 3.1.1.模拟命令

使用**simu** 功能完成

以配置文件或仅包含配置文件的文件夹为输入，若传入多个配置文件，文件间应用”，“分割。输出为基于配置文件内参数生成的模拟数据。

配置文件应命名为"\<name\>\_"configure.txt，输出的模拟数据为 "\<name\>\_simulation"。其中，\<name\>为用户自定义文件名。



**参数说明：**

使用 **-i** 参数传入文件夹或文件的路径

使用 **-o** 参数设置输出文件夹路径



**示例:**

- 以仅包含配置文件的文件夹为输入：基于simu 文件夹下的配置文件进行数据模拟，并存储于simu_data文件夹下。

```shell
python3.8 DASD.py simu -i simu_config/ -o simu_data
```

- 以配置文件为输入：

```shell
python3.8 DASD.py simu -i simu_config/chSel_configure.txt -o simu_data
```




### 3.1.2.模拟数据配置文件说明


配置文件见DASD/simu_config 文件夹下，包含经典选择性扫除、与经典选择性扫除连锁、温和选择性扫除、与温和选择性扫除连锁、中性 5个类别的配置文件，每个类别数据对应一个配置文件。需考虑的配置参数包含：

- rep：模拟次数（默认为2500，表示进行2500次模拟，生成2500组选择信号模拟数据）
- hap：染色体条数（默认为100）
- len：染色体片段长度（默认为100kbp，discoal软件最大长度为220kbp，若需模拟更长的片段，需重新编译discoal软件。见3.1 ）
- Pt：突变率取值范围，由上限和下限两个数值组成，需用户提供。
- Pr：重组率取值范围，由上限和下限两个数值组成，需用户提供。
- Pu：选择结束时间和抽样时间的间隔（默认为0.0005982817348574893 0）
- Pa：选择强度取值范围，由上限和下限两个数值组成，需用户提供。
- Px：受选择位点发生区域（默认为0.475 0.525，即，受选择位点位于片段的0.475-0.525内）
- Pxx：受选择位点不连续，使用该参数，默认为（0-0.475 0.525-1）
- en：群体历史参数，需用户提供。格式为 **en  t  0  N~t~/N~a~**，其中，t为向前回溯的时间，N~t~ 为 在t 时间的群体规模，N~a~ 为当前时间的群体规模。通过使用多个en参数完成对群体历史的表征（N随t的变化）。

配置文件第一列为所使用参数，后续列为参数值，列之间以空格或制表符分割。对于en 参数，由于往往具有多个，每个 en 参数为一行进行排列。



## 3.2.模拟数据特征工程

使用**calc_domain**功能完成，实现将模拟数据转化为特征矩阵。

**参数说明：**

- **-i** 或 **--input**：模拟数据文件所在文件夹，或单个或多个模拟数据文件（以','为分割符）
- **-o** 或 **--out**：输出文件夹

**可选参数：**

- **--filter** : 设置剔除样本的标准，即剔除SNP少于250的样本，默认为250
- **--core** : 设置使用CPU数，建议使用8的倍数，且不应超过n*8，n为传入的文件数(或文件夹内的文件数)，默认为16



**示例:** 将simu_data下模拟数据转化为特征矩阵，并存储于simu_feature文件夹下。

```shell
python3.8 DASD.py calc_domain -i simu_data --filter 250 --core 16 -o simu_feature
```



## 3.3. 真实数据特征工程

使用**calc_target** 功能完成，与3.2部分传入参数相同，用于将真实基因组数据转化为特征矩阵。

**参数说明：**

- **-i** 或 **--input**：模拟数据文件所在文件夹，或单个或多个模拟数据文件（以','为分割符）
- **-o** 或 **--out**：输出文件夹

**可选参数：**

- **--filter** : 设置剔除样本的标准，即剔除SNP少于250的样本，默认为250
- **--core** : 设置使用CPU数，建议使用8的倍数，且不应超过n*8，n为传入的文件数(或文件夹内的文件数)，默认为16
- **--start** ： 若仅对染色体部分片段转化为特征图，通过设定该参数，指定转换的起始位置，默认为None
- **--end**：通过设定该参数，指定转换的终止位置，默认为None



**示例:**将real_data下模拟数据转化为特征矩阵，并存储于real_feature文件夹下。

```shell
python3.8 DASD.py calc_domain -i real_data --filter 250 --core 16 -o real_feature
```



## 3.4. 数据标注

使用**data_annotation**完成，根据用户提供的配置文件构建用于模型训练的数据集。

**参数说明：**

- **-i** 或 **--input**：模拟数据特征矩阵文件所在文件夹，或单个或多个模拟数据特征矩阵文件（以','为分割符）（即，3.2输出结果）
- **--config** : 配置文件，包含标注信息
- **-o** 或 **--out**：输出文件夹，用于存储输出的模型训练数据集



**示例：**根据用户提供的配置文件，使用simu_feature下的特征矩阵构建训练数据集。生成的数据集存储于trainSet文件夹下。

```shell
python3.8 DASD.py data_annotation -i simu_feature --config label_configure.txt -o trainSet
```



**配置文件说明：**

配置文件见DASD/label_configure.txt，由两列构成，第一列为用户在3.1.2中自定义的配置文件的\<name\> ， 第二列为该类别对应的标签。

Note：标签使用连续的整数型数字，且应从0开始。即，若包含n类数据(假设n > 1)，则标签应由 0 ，1 ，,,,，n构成。

## 3.5.模型训练

使用**train**完成

**参数说明：**

- **--train-data** : 训练集数据所在路径
- **--train-label** : 训练集标签所在路径
- **--valid-data** : 验证集数据所在路径
- **--valid-label**: 验证集标签所在路径
- **--test-data** ：测试集数据所在路径
- **--test-label** ： 测试集标签所在路径
- **-t**或 **--target** ： 目标域数据集所在路径
- **-o**或 **--out** ： 模型输出文件夹所在路径

**可选参数：**

**-a** 或 **--all** : 0 或1，0表示仅输出最优模型，1表示输出迭代过程生成的所有模型。默认为0

**-M**： 子模型的个数，推荐使用5，默认为5。



**demo:** 传入训练、验证、测试数据集及真实数据特征矩阵，将训练完成后的模型输出至Ensemble_CEU 文件夹下。

```shell
python3.8 DASD.py train --train-data trainSet/trainSet.npy --train-label trainSet/trainSet_label.npy --valid-data trainSet/validSet.npy --valid-label trainSet/validSet_label.npy --test-data trainSet/testSet.npy --test-label trainSet/testSet_label.npy -t real_feature/ -o ../Ensemble_CEU
```



## 3.6.预测

使用**pred**完成

**参数说明**

- **-m** 或 **--model**: 模型所在路径
- **-M** : 子模型个数，应与3.5中指定M一致，默认为5
- **-f** 或 **--feature**: 待预测数据特征矩阵所在路径（3.3输出结果，以 vcf_featureMap.npy 结尾的文件）
- **-p** 或 **--position**: 待预测数据对应的位置信息（3.3输出结果以 vcfposInfo 结尾的文件）
- **-o** 或 **--out** ： 预测结果



**示例：** 对CEU.chr2.vcf_featureMap.npy（CEU群体2号染色体）进行预测

```shell
python3.8 DASD.py pred -m ../Ensemble_CEU_ensemble/ -M 5 -f real_feature/CEU.chr2.vcf_featureMap.npy -p real_feature/CEU.chr2.vcfposInfo -o pred_res/CEU.chr2.pred.txt
```



# 4.输出结果说明

以 CEU.chr2.vcf_featureMap.npy 的输出结果为例：

![image](https://github.com/soo-h/DASweepDetect/assets/74720083/8b4670b6-0961-4073-a8b7-c5df89613e8e)

 <p align="center"><b>（输出文件）</b></p>

第一列为判定区域的左端点，第二列为判定区域的右端点。第三列为判别类型，第四列为预测概率，第五列为分别预测为五个类别的概率。

以第一行为例，460kbp-560kbp该区域被判定为未受到选择（DASD/label_configure.txt 中，标签 4 对应中性类）。

