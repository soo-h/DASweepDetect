# DASDC

## *Domain Adversarial Sweep Detection and Classification*

## _Note：The following contents will be added later:_

 _<1>*we will continue to add trained models as potential options to save the user's time*_.



## Configuration required for operation

Applicable platform: Linux

Resource requirement: Since model training requires a lot of resources, we recommend using 8 cpus, 18GB of memory, and 200GB of hard disk storage to operation DASDC at least.



## Contents

- **OVERVIEW**
- **GETTING STARTED**
- **USAGE**
- **OUTPUT**
- **FAQ**



# **OVERVIEW**

 `DASDC` is a software that utilizes deep learning (specifically, domain adversarial networks) to identify and classify selective sweeps. By incorporating an adversarial learning module to extract useful invariant representations between simulated training data and real data, it outperforms traditional statistical methods. As a result, `DASDC` demonstrates higher generalization in detecting and classifying selective sweeps in real data.

`DASDC` only supports the analysis of selective sweeps for a single population. With input of a **single population `VCF` file** and **`population genetic parameters`** and **`Demographic` of the population**, the software performs six steps to accomplish the identification and classification of selective sweep.

![image](https://github.com/soo-h/DASweepDetect/assets/74720083/a1205262-6a17-4ec3-84fb-5e82bb92ca4c)
 <p align="center"><b>（DASDC work diagram）</b></p>


If you identify any bugs or issues with the software, then please contact  to report the issue.

If you use this software, then please cite it as ……

# **GETTING STARTED**

**Note:**`DASDC` was developed based on Python 3.8. Due to the use of certain features specific to Python 3.8, it currently requires Python 3.8 to run. In the future, optimizations will be made to ensure compatibility with other versions of Python 3.

1.python3.8 instsall

install python on the command line enter:

```shell
wget https://www.python.org/ftp/python/3.8.6/Python-3.8.6.tgz
tar -zxvf Python-3.8.6.tgz
cd Python-3.8.6

./configure --prefix=$PATH #Specifies the path of python installation

make
make install
```

$PATH is installation path of python



2.Create virtual environment（**Not necessary**）

Suggestion: Create a virtual environment to prevent conflicts between DASDC and other project dependency libraries.


   ```shell
python3.8 -m venv dasdc_env  # create virtual environment
source dasdc_env/bin/activate  # activate virtual environment
   ```



3.Software and dependency package installation

<1> DASDC download

```shell
git clone https://github.com/soo-h/DASweepDetect
```

<2>Run the following command to install the third-party dependency  libraries for DASDC

```shell
pip3.8 install -r require.txt
```
**Note:  If the pip installation fails**,user can download DASDC_dependency.tar.gz from https://data.mendeley.com/datasets/vdg2nbpc4j and unzip the third-party package under  $PATH/lib/python3.8/site-packages.(\$PATH is the path of the virtual environment). 

<3>Set executable permissions for `discoal`:

```shell
chmod 755 discoal
```



# USAGE

The identification and classification of the selective sweeps are completed by performing the following six steps in sequence:

- step1. Simulate training dataset 
- step2. Feature engineering for simulated training dataset
- step3. Feature engineering for real genomic dataset
- step4. Data annotation
- step5. Model training
- step6. Predict

**Note: the demo input/output files are readily accessible at https://data.mendeley.com/datasets/vdg2nbpc4j**

## Step1.Simulate dataset for model training
Use `simu` function to generate  simulated training data based on real genome data.

We put the compiled binary package of `discoal` into the code repository and complete the data simulation by calling `discoal ` software. If you need to recompile, download it from the link below and recompile it:

https://github.com/kr-colab/discoal

Citations

- Andrew D. Kern, Daniel R.     Schrider, Discoal: flexible coalescent simulations with selection,     Bioinformatics, Volume 32, Issue 24, december 2016, Pages 3839–3841, https://doi.org/10.1093/bioinformatics/btw556.



### <1>Command

Input a configuration file or a folder containing only configuration files. If multiple configuration files are inputted, please split them by using  commas . The output is simulated data generated based on the parameters specified in the configuration file. The configuration file should be named "\<name\>\_"configure.txt and the output simulation data should be "\<name\>\_simulation". \<name\> is the file name defined by the user.

**Parameter description：**

**-i :** The path of input folder or file

**-o :** The path of output folder or file



**Demo:**

- Take a folder containing only configuration files as input: Data is simulated based on configuration files in the simu folder and stored output in the simu_data folder.

```shell
python3.8 DASD.py simu -i simu_config/ -o simu_data
```

- Take the configuration file as input and stored output in the simu_data folder：

```shell
python3.8 DASD.py simu -i simu_config/chSel_configure.txt -o simu_data
```



### <2>Configuration file format description

The configuration demo files can be found in the example/simu_config folder, which contains five types of configuration files: hard sweep; hard linkage sweep; soft sweep; soft linkage sweep and neutral. Each type of configuration file corresponds to one configuration file. Configuration parameters to consider include:

- rep：Simulation times (Default is 2500, which means 2500 simulations are performed and 2500 sets of selective sweep simulation data are generated)
- hap：The size of each simulated sample (Default is 100, which means 50 diploid individuals)
- len：Length of chromosome fragments (Default is 100kbp, maximum length of discoal software is 220kbp, if you need to simulate longer fragments, you need to recompile discoal software. See 3.1)
- Pt：The value range of mutation rate, consisting of upper and lower limit values, needs to be provided by the user.
- Pr：The value range of recombination rate, consisting of upper and lower limit values, needs to be provided by the user.
- Pu：The value of  the selection end time and sampling time (Default is 0.0005982817348574893 0).
- Pa：The value range of coefficience of selection , consisting of upper and lower limit values, needs to be provided by the user.
- Px：The region where the selective site occurs (default is 0.475 0.525, that is, the selected site is within 0.475 to 0.525 of the fragment)
- Pxx：Use this parameter to specify the occurrence location of the selection when the selective site occurs region consist of  discontinuous intervals. (Default is (0-0.475 0.525-1), which means selective site occurs in 0-0.475 or 0.525-1).
- en：Demographic parameters need to be provided by the user. The format is **en t 0 N~~t~~/N~~a~~**, where **t** represents the backward tracing time, **N~~t~~** represents the group size at time **t**, and **N~~a~~** represents the group size at the current time. By using multiple en parameters, the representation of group history (N varying with t) can be achieved.

The first column of the configuration file represents the used parameters , and the subsequent columns represent the parameter values. Columns are separated by spaces or tabs. For the **en** parameter, since there are often multiple values, each en parameter is arranged on a separate line.

**For a specific population (breed/species), the mutation rate, recombination rate, selection strength, demographic history must be provided by the user, and the rest of the parameters we recommend using the default values. How to set the four required parameters see：**

**DASweepDetect/Parameter_Inference.md at main · soo-h/DASweepDetect (github.com)](https://github.com/soo-h/DASweepDetect/blob/main/Parameter_Inference.md)**



## Step2.Feature engineering for simulated dataset

Use `calc_domain`  to convert simulated data into feature matrix.

**Parameter description**

- **-i** or **--input**：path to the folder which contains the simulated data files, or one or more simulation data files (with`,`as the separator)
- **-o** or **--out**：the path of output folder or file

**Optional parameter**

- **--filter** : the criterion for rejecting samples rejecting samples with less than n SNPs. Default is 250.
- **--core** : the number of CPU cores used to program. Recommended value is a multiple of 8 and not suggest exceed n x 8(n is the number of input files or files in a folder). Default value is 16.



**Demo:** Convert the simulated data under the folder of simu_data into feature matrix and store it in the simu_feature folder.

```shell
python3.8 DASD.py calc_domain -i simu_data -o simu_feature
```

simu_data is a folder, which contains only simulated data; simu_feature is a folder, which stores  output feature file that correspondence with the input simulated data.

## Step3.Feature engineering for real genomic data

Use the `calc_target` function to convert the real genome data into the feature matrix. 

**Parameter description：**

- **-i** or **--input**：Path to the folder which contains the  real data files  of **VCF** format and composed of a single chromosome , or one or more real data files of  **VCF** format and composed of a single chromosome (with `,` as the separator).
- **-o** or **--out**：the path of output folder or file

**Optional parameter：**

- **--filter** : The criterion for rejecting samples rejecting samples with less than n SNPs , this value must greater than or equal to 250. Default is 250.
- **--window-size** : The windows size of convert feature map. The parameter determines the size of genomic information the model utilizes for each learning and prediction. Default=1000000
- **--window-step** : The step of windows. The parameter determines the size of the region that the model prediction each time. Default is window_size / 20, i.e., 50000. 

- **--core** : The number of CPU cores used to program. Recommended value is a multiple of 8 and not suggest exceed n x 8. n is the number of input files (or files in a folder). Default value is 16.
- **--start** ： use this parameter to convert part of the chromosome  to a feature map,need provide the start position. Default position is None.
- **--end**：use this parameter to convert part of the chromosome  to a feature map,need provide the end position. Default position is None

**Demo:**  Convert the real genome data under the "real_data" folder into feature matrix and store them in the "real_feature" folder.

```shell
python3.8 DASD.py calc_target -i real_data -o real_feature
```

The real_data folder should contain real genomic data for selective sweep analysis in VCF format, split by chromosome. It needs to be created by the user. The simu_feature is a folder, which stores  output feature file that correspondence with the input VCF data.\
**Note:** In this example, the model will perform selective sweep prediction on regions of 50k, and utilizes an additional 475k of upstream and downstream information for each region.

## Step4.Data labeling for simulated dataset

Use the `data_annotation` function to construct a dataset for model training based on the configuration file provided by user.

**Parameter description：**

- **-i** or **--input**：path of folder which contain the simulated data feature matrix files, or a single or multiple simulated data feature matrix files (separated by `,`) (i.e., output results from step 2).
- **--config** : path of configure file，which contain annotation infomation.
- **-o** or **--out**：path of output folder which store the generated model training dataset.



**Demo：** Using the feature matrix under the "simu_feature" folder construct a training dataset based on the configuration file provided by the user. The generated dataset will be stored in the "trainSet" folder.

```shell
python3.8 DASD.py data_annotation -i simu_feature --config label_configure.txt -o trainSet
```

simu_feature is a folder, which contains only feature matrix of simulated data with .npy format;  trainSet is a folder, which stores dataset  that generated by simulated feature matrix.

**Configuration file description：**

The configuration file can be found at example/label_configure.txt, which consists of two columns. The first column represents the <name> of the custom configuration file specified by the user in step1, and the second column represents the corresponding label for that class.

**Note:** The labels are represented by consecutive integers starting from 0. If there are n classes of data (assuming n > 1), the labels should range from 0 to n-1.

## Step5.Model training

Use the `train` function to train model for detecting and classifying selective sweeps in a specific population.

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

**-M**： The number of ensemble models. It is recommended to use 5. Default value is 5.



**Demo:** Input the training, validation, testing datasets and labels (all this generate in step4), and the real data feature matrix(generate in step3). Output the  trained model to the "Ensemble_CEU" folder.

```shell
python3.8 DASD.py train --train-data trainSet/trainSet.npy --train-label trainSet/trainSet_label.npy --valid-data trainSet/validSet.npy --valid-label trainSet/validSet_label.npy --test-data trainSet/testSet.npy --test-label trainSet/testSet_label.npy -t real_feature/ -o ../Ensemble_CEU
```



## Step6.Prediction

Use `pred` complete. Use this function to output selective sweep detection and classification results.

**Parameter description**

- **-m** or **--model**: Path of folder which contains the  sub-models which used ensemble.
- **-M** : The number of ensemble models. Default is 5.
- **-f** or **--feature**: Path of the feature matrix for the data to be predicted.（the output of step3 ，ending with "vcf_featureMap.npy"）
- **-p** or **--position**: Path of the position information for the data to be predicted.（the output of step3 , ending with " vcfposInfo "）
- **-o** or **--out** ： Path of pred result.



**Demo:** Perform prediction on CEU.chr2.vcf_featureMap.npy (Chromosome 2 of CEU population).

```shell
python3.8 DASD.py pred -m ../Ensemble_CEU_ensemble/ -M 5 -f real_feature/CEU.chr2.vcf_featureMap.npy -p real_feature/CEU.chr2.vcfposInfo -o pred_res/CEU.chr2.pred.txt
```

../Ensemble_CEU_ensemble/ is the path of folder which contain multi sub-models; The value after M corresponds to the number of models the folder contains. real_feature/CEU.chr2.vcf_featureMap.npy and real_feature/CEU.chr2.vcfposInfo is the output of step3, which are the feature and position information with single chromosome  respectively. 

For whole-genome prediction, each chromosome needs to be predicted separately. It means, if you have ten chromosome  to predict, you need to execute step6 ten times.



# Output

## Output file description

Taking the output results of CEU.chr2.vcf_featureMap.npy as example :

![image](https://github.com/soo-h/DASweepDetect/assets/74720083/dfe357d9-7e9f-4474-9686-5078228cb314)

 <p align="center"><b>（output file）</b></p>

The first column represents the left endpoint of the predicted region. The second column represents the right endpoint of the predicted region. The third column represents the classification type. The fourth column represents the predicted probability. The fifth column represents the probability of being predicted for each of the five categories.

Taking the first row as an example, the region from 485kbp to 535kbp is determined to be neutral class (according to the label 4 in label_configure.txt).

## Calibrate prediction result

Regarding the prediction results, if the DASDC method identifies a genomic region as undergoing a hard sweep (or hard linkage sweeps), we have complete confidence in the reliability of these predictions. Therefore, genes enriched within this region can be considered for subsequent functional verification studies. In compare with hard sweeps (or hard linkage sweeps), a relatively higher false positive rate in the detection of soft sweeps (or soft linkage sweeps). Therefore, we recommend implementing a more stringent quality control criterion by choosing only the top 5% of predicted soft sweeps across the whole genome for further analysis. 

Regarding the highlighting of selective sweep detection results, we posit that linkage class differentiation serves primarily to subdivide and further reduce false positive rates in both hard and soft sweeps. Furthermore, the significance of linkage classes lies in their ability to support hard and soft sweeps. Therefore, in order to achieve a more intuitive graphical effect when highlighting the prediction results of hard sweeps, we suggest considering adding the prediction probabilities of hard sweep and its linkage. As for soft sweeps, due to their higher false positive rate with soft linkage, we recommend only using predicted soft sweeps for highlighting.

# AVAILABLE MODELS

We put some models trained for specific species (or populations) in  https://data.mendeley.com/datasets/vdg2nbpc4j,  users can directly select the model corresponding to the population to be studied for the detection and classification of the selective sweep .

**This process is done in the following two steps:**

- step1: Feature engineering for real genomic data (detail see USAGE: Feature engineering for real genomic data)

The input is folder which constitute of contains only one chromosome VCF format files.  If genome-wide data is used, it needs to be split into multiple files by chromosome.

- step2: Prediction (detail see USAGE: Prediction)

Make predictions about the feature of one chromosome. To predict genome-wide data,it needs to predict chromosome feature separately.

**Demo:**

- step1: get real feature matrix.

```python
python3.8 DASD.py calc_target -i real_data -o real_feature
```
real_data is folder which contain input data with **VCF** format; real_feature is output folder which contain output feature of input VCF file, and one chromosome corresponds to one output feature file.

- step2: get predict result.

```python
python3.8 DASD.py pred -m MODEL_PATH -M 5 -f real_feature/CEU.chr2.vcf_featureMap.npy -p real_feature/CEU.chr2.vcfposInfo -o pred_res/CEU.chr2.pred.txt
```

MODEL_PATH is the path of folder which contain multi sub-models. The value after M corresponds to the number of models the folder contains. real_feature/CEU.chr2.vcf_featureMap.npy and real_feature/CEU.chr2.vcfposInfo is the output of step1, .which are the feature and position information with single chromosome  respectively. 

For whole-genome prediction, each chromosome needs to be predicted separately. It means, if you have ten chromosome  to predict, you need to execute step2 ten times

## Homo sapiens

### <1>CEU Model

**Description:** Model for detection and classification selective sweep of Utah residents  with Northern and Western European ancestry population.

**Location:** Homo_sapiens/CEU

**Citations:**



## Sus scrofa domestica

### <1> LW Model

**Description:** Model for detection and classification selective sweep of Large White pig population.

**Location:** Sus_scrofa/LW

**Citations:**

## Anopheles gambiae

### <1> BFS Model

**Description:** Model for detection and classification selective sweep of A. gambiae from Burkina Faso population.

**Location:** Anopheles_gambiae/BFS

**Citations:**



# FAQ

