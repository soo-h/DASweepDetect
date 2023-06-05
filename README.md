# DASDC

## *Domain Adversarial Sweep Detection and Classification*

### **_Note：The software is still being updated._**

**_The following contents will be added later:_ ** 

_<1>detailed population genetic parameters steps;_

_<2>models that can be used for detection and classification of specific selective sweep;_

_<3>detailed explanation of model output results and visualization scripts._

## Contents

- **OVERVIEW**
- **GETTING STARTED**
- **USAGE**
- **OUTPUT**
- **FAQ** 



# **OVERVIEW**

 `DASDC` is a software based on deep learning (domain adversarial networks) for selective sweep identification and classification. It outperforms traditional statistical methods in terms of performance and introduces an adversarial learning module to extract useful invariant representations between simulated and real data. As a result, `DASDC` demonstrates higher generalization in the detection and classification of selective sweep in real genomic data.

`DASDC` only supports selection signal analysis for a single population. With input of a **single population `VCF` file** and **`population genetic parameters` and `Demographic` of the population**, the software performs six steps to accomplish the identification and classification of selective sweep.

![image](https://github.com/soo-h/DASweepDetect/assets/74720083/a1205262-6a17-4ec3-84fb-5e82bb92ca4c)
 <p align="center"><b>（DASDC work diagram）</b></p>


If you identify any bugs or issues with the software, then please contact  to report the issue.

If you use this software, then please cite it as

# **GETTING STARTED**

**Note: **`DASDC` was developed based on Python 3.8. Due to the use of certain features specific to Python 3.8, it currently requires Python 3.8 or higher to run. In the future, optimizations will be made to ensure compatibility with other versions of Python 3.

1.python3.8 instsall

install python on the command line enter:

```shell
wget https://www.python.org/ftp/python/3.8.6/Python-3.8.6.tgz
tar -zxvf Python-3.8.6.tgz
cd Python-3.8.6

./configure --prefix=$PATH

make
make install
```

$PATH is installation path of python



2.Create virtual environment（Not necessary）

**Suggestion: Create a virtual environment**


   ```shell
python -m venv my_project_env  # create virtual environment
source my_project_env/bin/activate  # activate virtual environment
   ```



3.Software and dependency package installation

```shell
git clone https://github.com/soo-h/DASweepDetect
```

Run the following command to install the third-party libraries that the software depends on

```shell
pip3.8 install -r require.txt
```
Set executable permissions for `discoal`:

```shell
chmod 755 discoal
```



# USAGE

- step1. Data simulation
- step2. Simulation data feature engineering
- step3. Real genome data feature engineering
- step4. Data annotation
- step5. Model training
- step6. Predict



## Data simulation
We put the compiled binary package of `discoal` into the code repository and complete the data simulation by calling `discoal ` software. If you need to recompile, download it from the link below and recompile it:

https://github.com/kr-colab/discoal

Citations

- Kern AD and Schrider DR 2016. https://doi.org/10.1093/bioinformatics/btw556



### <1>Command

Use the `simu` function to complete.

Input a configuration file or a folder containing only configuration files. If multiple configuration files are input, apply split files by  `,` . The output is simulated data generated based on the parameters in the configuration file.

The configuration file should be named "\<name\>\_"configure.txt and the output simulation data should be "\<name\>\_simulation". \<name\> is the file name defined by the user.

**Parameter description：**

**-i :** The path of input folder or file

**-o :** The path of output folder or file



**Demo:**

- Take a folder which containing only configuration files as input: Data is simulated based on configuration files in the simu folder and stored output in the simu_data folder.

```shell
python3.8 DASD.py simu -i simu_config/ -o simu_data
```

- Take the configuration file as input：

```shell
python3.8 DASD.py simu -i simu_config/chSel_configure.txt -o simu_data
```



### <2>Configuration file description of simulation data 

Configuration files can be found in the DASD/simu_config folder, which contains five types of configuration files: hard sweep; hard linkage sweep; soft sweep; soft linkage sweep and neutral. Each type of configuration file corresponds to one configuration file. Configuration parameters to consider include:

- rep：Simulation times (Default is 2500, which means 2500 simulations are performed and 2500 sets of selective sweep simulation data are generated)
- hap：Chromosome numbers contained in the population genome (Default is 100)
- len：Length of chromosome fragments (Default is 100kbp, maximum length of discoal software is 220kbp, if you need to simulate longer fragments, you need to recompile discoal software. See 3.1)
- Pt：The value range of mutation rate, consisting of upper and lower limit values, needs to be provided by the user.
- Pr：The value range of recombination rate, consisting of upper and lower limit values, needs to be provided by the user.
- Pu：The value of  the selection end time and sampling time (Default is 0.0005982817348574893 0).
- Pa：The value range of coefficience of selection , consisting of upper and lower limit values, needs to be provided by the user.
- Px：The region where the selective site occurs (default is 0.475 0.525, that is, the selected site is within 0.475 to 0.525 of the fragment)
- Pxx：Use this paramater when the selected sites are not contiguous. (Default is  (0-0.475 0.525-1)).
- en：Demographic parameters need to be provided by the user. The format is **en t 0 N~~t~~/N~~a~~**, where **t** represents the backward tracing time, **N~~t~~** represents the group size at time **t**, and **N~~a~~** represents the group size at the current time. By using multiple en parameters, the representation of group history (N varying with t) can be achieved.

The first column of the configuration file represents the parameters used, and the subsequent columns represent the parameter values. Columns are separated by spaces or tabs. For the en parameter, since there are often multiple values, each en parameter is arranged on a separate line.

## Simulation data feature engineering

Use `calc_domain`  to convert simulated data into feature matrix.

**Parameter description**

- **-i** or **--input**：path to the folder where the simulated data file is located, or one or more simulation data files (with`,`as the separator)
- **-o** 或 **--out**：the path of output folder or file

**Optional parameter**

- **--filter** : the criterion for rejecting samples rejecting samples with less than n SNPs. Default is 250.
- **--core** : the number of CPU cores used to program. Recommended value is a multiple of 8 and not suggest exceed n x 8. n is the number of input files (or files in a folder). Default value is 16.

**Demo:** Convert the simulated data under the folder of simu_data into feature matrix and store it in the simu_feature folder.

```shell
python3.8 DASD.py calc_domain -i simu_data --filter 250 --core 16 -o simu_feature
```



## Real data feature engineering

Use the `calc_target` function to convert the real genome data into the feature matrix. which is the same as the passed parameter in step2.

**Parameter description：**

- **-i** or **--input**：Path to the folder where the  real data file is located, or one or more simulation data files (with `,` as the separator)
- **-o** or **--out**：the path of output folder or file

**Optional parameter：**

- **--filter** : The criterion for rejecting samples rejecting samples with less than n SNPs. Default is 250.
- **--window-size** : The windows size of convert feature map. Default=100000
- **--window-step** : The step of windows. Default=None

- **--core** : The number of CPU cores used to program. Recommended value is a multiple of 8 and not suggest exceed n x 8. n is the number of input files (or files in a folder). Default value is 16.
- **--start** ： use this parameter to convert part of the chromosome  to a feature map,need provide the start position. Default position is None.
- **--end**：use this parameter to convert part of the chromosome  to a feature map,need provide the end position. Default position is None

**Demo:**  Convert the simulated data under the "real_data" folder into feature matrix and store them in the "real_feature" folder.

```shell
python3.8 DASD.py calc_target -i real_data --filter 250 --core 16 -o real_feature
```



## Data annotation

use `data_annotation` complete，which constructing a dataset for model training based on the configuration file provided by the user.

**Parameter description：**

- **-i** or **--input**：path of folder which contain the simulated data feature matrix files, or a single or multiple simulated data feature matrix files (separated by `,`) (i.e., output results from step 2).
- **--config** : path of configure file，which contain annotation infomation.
- **-o** or **--out**：path of output folder which store the generated model training dataset.



**Demo：** Using the feature matrix under the "simu_feature" folder, construct a training dataset based on the configuration file provided by the user. The generated dataset will be stored in the "trainSet" folder.

```shell
python3.8 DASD.py data_annotation -i simu_feature --config label_configure.txt -o trainSet
```



**Configuration file description：**

The configuration file can be found at DASD/label_configure.txt, which consists of two columns. The first column represents the <name> of the custom configuration file specified by the user in step1, and the second column represents the corresponding label for that class.

**Note:** The labels are represented by consecutive integers starting from 0. If there are n classes of data (assuming n > 1), the labels should range from 0 to n-1.

## Model training

Use `train` complete.   This function use for model training.

**Parameter description：**

- **--train-data** : Path of the training dataset.
- **--train-label** : Path of the training label.
- **--valid-data** : Path of the valid dataset.
- **--valid-label**: Path of the valid label.
- **--test-data** ：Path of the test dataset.
- **--test-label** ： Path of the test label.
- **-t** or **--target** ：  Path of the domain of target dataset.
- **-o** or **--out** ： Path of the output folder for the model.

**Optional parameter**

**-a** or **--all** : 0 or 1, where 0 indicates outputting only the best model and 1 indicates outputting all models generated during iterations. Default value is 0.

**-M**： The number of sub-models. It is recommended to use 5. Default value is 5.



**Demo:** Input the training, validation, and testing datasets, along with the real data feature matrix, and output the trained model to the "Ensemble_CEU" folder.

```shell
python3.8 DASD.py train --train-data trainSet/trainSet.npy --train-label trainSet/trainSet_label.npy --valid-data trainSet/validSet.npy --valid-label trainSet/validSet_label.npy --test-data trainSet/testSet.npy --test-label trainSet/testSet_label.npy -t real_feature/ -o ../Ensemble_CEU
```



## Prediction

Use `pred` complete. Use this function to output selective sweep detection and classification results.

**Parameter description**

- **-m** or **--model**: Path of model.
- **-M** : The number of sub-model,should consistent with the provided number of sub-models. Default is 5.
- **-f** or **--feature**: Path of the feature matrix for the data to be predicted.（the output of step3 ，ending with "vcf_featureMap.npy"）
- **-p** or **--position**: Path of the position information for the data to be predicted.（the output of step3 , ending with " vcfposInfo "）
- **-o** or **--out** ： Path of pred result.



**Demo:** Perform prediction on CEU.chr2.vcf_featureMap.npy (Chromosome 2 of CEU population).

```shell
python3.8 DASD.py pred -m ../Ensemble_CEU_ensemble/ -M 5 -f real_feature/CEU.chr2.vcf_featureMap.npy -p real_feature/CEU.chr2.vcfposInfo -o pred_res/CEU.chr2.pred.txt
```



# OUTPUT

Taking the output results of CEU.chr2.vcf_featureMap.npy as example :

![image](https://github.com/soo-h/DASweepDetect/assets/74720083/8b4670b6-0961-4073-a8b7-c5df89613e8e)

 <p align="center"><b>（output file）</b></p>

The first column represents the left endpoint of the predicted region. The second column represents the right endpoint of the predicted region. The third column represents the classification type. The fourth column represents the predicted probability. The fifth column represents the probability of being predicted for each of the five categories.

Taking the first row as an example, the region from 460kbp to 560kbp is determined to be neutral class (according to the label 4 in label_configure.txt).



# AVAILABLE MODELS

We put some models trained for specific species and groups in `available_models` folder,  users can directly select the model corresponding to the population to be studied for the detection and classification of the selective sweep (call USAGE-Prediction).

## Homo sapiens

### <1>CEU Model

**Description:** Model for detection and classification selective sweep of CEU population.

**Location:** available_models/Homo_sapiens/CEU

**Citations:**



## Sus scrofa domestica

### <1> LW Model

**Description:** Model for detection and classification selective sweep of CEU population.

**Location:** available_models/Sus_scrofa/LW

**Citations:**

## Anopheles gambiae

### <1> BFS Model

**Description:** Model for detection and classification selective sweep of CEU population.

**Location:** available_models/Anopheles_gambiae/BFS

**Citations:**



# FAQ

