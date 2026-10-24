=====
DASDC
=====

*Domain Adversarial Sweep Detection and Classification*

.. note::

   The following contents will be added later:

   - We will continue to add trained models as potential options to save the user's time.

-----------------------------------------------------------------------
Configuration Required for Operation
-----------------------------------------------------------------------

**Applicable platform:** Linux

**Resource requirement:** Since model training requires a lot of resources, we recommend using at least 8 CPUs, 18 GB of memory, and 200 GB of hard disk storage to operate DASDC.

-----------------------------------------------------------------------
Contents
-----------------------------------------------------------------------

- **OVERVIEW**
- **GETTING STARTED**
- **USAGE**
- **OUTPUT**
- **FAQ**

-----------------------------------------------------------------------
Overview
-----------------------------------------------------------------------

DASDC is software that uses deep learning, specifically domain-adversarial neural networks, to identify and classify selective sweeps. Its adversarial learning module extracts representations shared by simulated training data and real data, improving generalization under domain mismatch as reported in the `DASDC paper <https://doi.org/10.1002/advs.202304842>`_.

DASDC only supports the analysis of selective sweeps for a single population. With input of a **single population VCF file** and **population genetic parameters** and **Demographic of the population**, the software performs six steps to accomplish the identification and classification of selective sweep.

.. figure:: https://github.com/soo-h/DASweepDetect/assets/74720083/a1205262-6a17-4ec3-84fb-5e82bb92ca4c
   :alt: DASDC work diagram
   :align: center

   DASDC work diagram

Report bugs and usage problems through the `GitHub issue tracker <https://github.com/soo-h/DASweepDetect/issues>`_.

If you use this software, please cite: Hui Song, Jinyu Chu, Wangjiao Li, *et al.* A Novel Approach Utilizing Domain Adversarial Neural Networks for the Detection and Classification of Selective Sweeps. *Advanced Science*. 2024;11(14):e2304842. `doi:10.1002/advs.202304842 <https://doi.org/10.1002/advs.202304842>`_.

-----------------------------------------------------------------------
Getting Started
-----------------------------------------------------------------------

.. note::

   The DASDC package and command-line syntax support Python 3.8 or newer. The legacy TensorFlow 2.7 backend is limited to Python 3.8-3.9. The optional PyTorch backend supports newer Python versions when a compatible PyTorch wheel is available.

1. Python Installation
======================

For the TensorFlow backend, Python 3.8.20 is the recommended reproducible environment. Install it on the command line if it is not already available:

.. code-block:: shell

   wget https://www.python.org/ftp/python/3.8.20/Python-3.8.20.tgz
   tar -zxvf Python-3.8.20.tgz
   cd Python-3.8.20

   DASDC_PYTHON_PREFIX=/absolute/path/to/python-3.8.20
   ./configure --prefix="$DASDC_PYTHON_PREFIX"
   make -j8
   make altinstall
   export PATH="$DASDC_PYTHON_PREFIX/bin:$PATH"
   python3.8 --version

Replace ``/absolute/path/to/python-3.8.20`` with a writable absolute installation directory. Do not use ``$PATH`` as the installation prefix; ``PATH`` is the shell's executable search list.

2. Create Virtual Environment (Optional)
=========================================

Suggestion: Create a virtual environment to prevent conflicts between DASDC and other project dependency libraries.

.. code-block:: shell

   python3.8 -m venv dasdc_env   # create virtual environment
   source dasdc_env/bin/activate # activate virtual environment

3. Software and Dependency Package Installation
===============================================

**Step 1: DASDC download**

.. code-block:: shell

   git clone https://github.com/soo-h/DASweepDetect
   cd DASweepDetect

**Step 2:** Install compatible dependencies and the editable DASDC command-line package:

.. code-block:: shell

   python -m pip install -e .

The editable installation uses the scripts and ``discoal`` executable in this clone. Do not move or delete the repository without reinstalling DASDC. Every command below can also be invoked as ``python -m dasdc <command>``.

For PyTorch GPU training, install a CUDA-enabled PyTorch build matching the system driver before installing DASDC. For example, PyTorch 2.2.2 with CUDA 12.1 can be installed with:

.. code-block:: shell

   python -m pip install torch==2.2.2 --index-url https://download.pytorch.org/whl/cu121
   python -m pip install -e .

Use the `official PyTorch installation selector <https://pytorch.org/get-started/locally/>`_ when a different CUDA or Python version is required. The package extra ``python -m pip install -e '.[pytorch]'`` is also available when the default package index provides the required build.

.. note::

   If pip installation fails, ``DASDC_dependency.tar.gz`` is available from `Mendeley Data <https://data.mendeley.com/datasets/vdg2nbpc4j>`_. It contains legacy, platform-specific packages and should be used only with a compatible Linux x86-64 Python 3.8 environment. Locate the active environment's package directory with ``python3.8 -c "import sysconfig; print(sysconfig.get_paths()['purelib'])"``; do not extract packages into the shell's ``$PATH`` value.

**Step 3:** Set executable permissions for ``discoal``:

.. code-block:: shell

   chmod 755 discoal

-----------------------------------------------------------------------
Usage
-----------------------------------------------------------------------

The identification and classification of the selective sweeps are completed by performing the following six steps in sequence:

- **Step 1:** Simulate training dataset
- **Step 2:** Feature engineering for simulated training dataset
- **Step 3:** Feature engineering for real genomic dataset
- **Step 4:** Data annotation
- **Step 5:** Model training
- **Step 6:** Predict

.. note::

   This repository contains the simulation and label configurations, but not the complete real-data workflow inputs. Supply single-population VCF or VCF.GZ files split by chromosome, or obtain the larger demonstration files from `Mendeley Data <https://data.mendeley.com/datasets/vdg2nbpc4j>`_.

-----------------------------------------------------------------------
Step 1: Simulate Dataset for Model Training
-----------------------------------------------------------------------

Use the ``simu`` function to generate simulated training data based on real genome data.

We put the compiled binary package of ``discoal`` into the code repository and complete the data simulation by calling ``discoal`` software. If you need to recompile, download it from the `discoal repository <https://github.com/kr-colab/discoal>`_.

**Citations:**

- Andrew D. Kern, Daniel R. Schrider, Discoal: flexible coalescent simulations with selection, *Bioinformatics*, Volume 32, Issue 24, December 2016, Pages 3839–3841, `doi:10.1093/bioinformatics/btw556 <https://doi.org/10.1093/bioinformatics/btw556>`_.

Command
=======

Input a configuration file or a folder containing only configuration files. If multiple configuration files are inputted, please split them by using commas. The output is simulated data generated based on the parameters specified in the configuration file. The configuration file should be named ``<name>_configure.txt`` and the output simulation data should be ``<name>_simulation``. ``<name>`` is the file name defined by the user.

**Parameter description:**

``-i``
   The path of input folder or file.

``-o``
   The path of output folder or file.

**Demo:**

- Take a folder containing only configuration files as input: Data is simulated based on configuration files in the ``simu`` folder and stored output in the ``simu_data`` folder.

.. code-block:: shell

   dasdc simu -i example/simu_config/ -o simu_data

- Take the configuration file as input and store output in the ``simu_data`` folder:

.. code-block:: shell

   dasdc simu -i example/simu_config/chSel_configure.txt -o simu_data

Configuration File Format Description
=====================================

The configuration demo files can be found in the ``example/simu_config`` folder, which contains five types of configuration files: hard sweep; hard linkage sweep; soft sweep; soft linkage sweep; and neutral. Each type of configuration file corresponds to one configuration file. Configuration parameters to consider include:

``rep``
   Simulation times (Default is 2500, which means 2500 simulations are performed and 2500 sets of selective sweep simulation data are generated).

``hap``
   The size of each simulated sample (Default is 100, which means 50 diploid individuals).

``len``
   Length of chromosome fragments (Default is 100 kbp, maximum length of discoal software is 220 kbp. If you need to simulate longer fragments, you need to recompile discoal — see `discoal source <https://github.com/kr-colab/discoal>`_).

``Pt``
   The value range of mutation rate, consisting of upper and lower limit values, needs to be provided by the user.

``Pr``
   The value range of recombination rate, consisting of upper and lower limit values, needs to be provided by the user.

``Pu``
   The value of the selection end time and sampling time (Default is 0.0005982817348574893 0).

``Pa``
   The value range of coefficient of selection, consisting of upper and lower limit values, needs to be provided by the user.

``Px``
   The region where the selective site occurs (default is 0.475 0.525, i.e., the selected site is within 0.475 to 0.525 of the fragment).

``Pxx``
   Use this parameter to specify the occurrence location of the selection when the selective site occurs region consists of discontinuous intervals. (Default is (0–0.475 0.525–1), which means selective site occurs in 0–0.475 or 0.525–1).

``en``
   Demographic parameters need to be provided by the user. The format is ``en t 0 Nt/Na``, where ``t`` represents the backward tracing time, ``Nt`` represents the group size at time ``t``, and ``Na`` represents the group size at the current time. By using multiple ``en`` parameters, the representation of group history (N varying with t) can be achieved.

The first column of the configuration file represents the used parameters, and the subsequent columns represent the parameter values. Columns are separated by spaces or tabs. For the ``en`` parameter, since there are often multiple values, each en parameter is arranged on a separate line.

.. important::

   For a specific population (breed/species), the mutation rate, recombination rate, selection strength, and demographic history **must be provided by the user**. The rest of the parameters we recommend using the default values.

   How to set the four required parameters — see: `Parameter_Inference.md <https://github.com/soo-h/DASweepDetect/blob/main/Parameter_Inference.md>`_

-----------------------------------------------------------------------
Step 2: Feature Engineering for Simulated Dataset
-----------------------------------------------------------------------

Use ``calc_domain`` to convert simulated data into feature matrix.

**Parameter description:**

``-i`` or ``--input``
   Path to the folder which contains the simulated data files, or one or more simulation data files (with ``,`` as the separator).

``-o`` or ``--out``
   The path of output folder or file.

**Optional parameters:**

``--filter``
   The criterion for rejecting samples with less than *n* SNPs. Default is 250.

``--core``
   The number of CPU cores used to program. Recommended value is a multiple of 8 and not suggest exceed *n* × 8 (*n* is the number of input files or files in a folder). Default value is 8.

**Demo:** Convert the simulated data under the ``simu_data`` folder into feature matrix and store it in the ``simu_feature`` folder.

.. code-block:: shell

   dasdc calc_domain -i simu_data -o simu_feature

``simu_data`` is a folder which contains only simulated data; ``simu_feature`` is a folder which stores output feature files that correspond with the input simulated data.

-----------------------------------------------------------------------
Step 3: Feature Engineering for Real Genomic Data
-----------------------------------------------------------------------

Use the ``calc_target`` function to convert the real genome data into the feature matrix.

**Parameter description:**

``-i`` or ``--input``
   Path to a folder containing phased, single-population **VCF** or **VCF.GZ** files split by chromosome, or one or more such files (with ``,`` as the separator). Phase genotypes before feature extraction.

``-o`` or ``--out``
   The path of output folder or file.

**Optional parameters:**

``--filter``
   Discard windows containing fewer than *n* SNPs. The default and recommended minimum is 250. The CLI accepts smaller values, but their use has not been validated by this project.

``--window-size``
   The genomic context used to construct each feature map and make each prediction. Default is 1000000 bp.

``--window-step``
   The distance between successive windows. Default is ``window_size / 20``, i.e., 50000 bp. It controls prediction spacing; the reported interval width is determined by the window size.

``--core``
   The number of CPU cores used by the program. Use a multiple of 8 where resources permit and do not exceed *n* × 8 (*n* is the number of input files or files in a folder). Default value is 8.

``--start``
   Use this parameter to convert part of the chromosome to a feature map. Need to provide the start position. Default is ``None``.

``--end``
   Use this parameter to convert part of the chromosome to a feature map. Need to provide the end position. Default is ``None``.

**Demo:** Convert the real genomic data under the ``real_data`` folder into feature matrices and store them in the ``real_feature`` folder.

.. code-block:: shell

   dasdc calc_target -i real_data -o real_feature

``real_data`` is a folder which contains only VCF format data with a single chromosome; ``real_feature`` is a folder which stores output feature files that correspond with the input VCF data.

Create ``real_data`` yourself and supply phased data split by chromosome. With the default 1 Mb window and 50 kb step, each prediction describes the central 50 kb interval using 475 kb of context on each side. Both prediction backends report the central 5% of each input window, so changing the step alone does not change the reported interval width.

-----------------------------------------------------------------------
Step 4: Data Labeling for Simulated Dataset
-----------------------------------------------------------------------

Use the ``data_annotation`` function to construct a dataset for model training based on the configuration file provided by the user.

**Parameter description:**

``-i`` or ``--input``
   Path of folder which contains the simulated data feature matrix files, or a single or multiple simulated data feature matrix files (separated by ``,``) — i.e., output results from Step 2.

``--config``
   Path of configure file, which contains annotation information.

``-o`` or ``--out``
   Path of output folder which stores the generated model training dataset.

**Demo:** Using the feature matrix under the ``simu_feature`` folder, construct a training dataset based on the configuration file provided by the user. The generated dataset will be stored in the ``trainSet`` folder.

.. code-block:: shell

   dasdc data_annotation -i simu_feature --config example/label_configure.txt -o trainSet

``simu_feature`` is a folder which contains only feature matrix of simulated data with ``.npy`` format; ``trainSet`` is a folder which stores the dataset generated by simulated feature matrix.

**Configuration file description:**

The configuration file can be found at ``example/label_configure.txt``, which consists of two columns. The first column represents the ``<name>`` of the custom configuration file specified by the user in Step 1, and the second column represents the corresponding label for that class.

.. note::

   The labels are represented by consecutive integers starting from 0. If there are *n* classes of data (assuming *n* > 1), the labels should range from 0 to *n* − 1.

-----------------------------------------------------------------------
Step 5: Model Training
-----------------------------------------------------------------------

Use the ``train`` function to train a model for detecting and classifying selective sweeps in a specific population.

**Parameter description:**

``--train-data``
   Path of the training dataset.

``--train-label``
   Path of the training label.

``--valid-data``
   Path of the valid dataset.

``--valid-label``
   Path of the valid label.

``--test-data``
   Path of the test dataset.

``--test-label``
   Path of the test label.

``-t`` or ``--target``
   Path of the domain of target dataset.

``-o`` or ``--out``
   Path of the output folder for the model.

**Optional parameters:**

``-s`` or ``--save``
   Checkpoint-retention flag accepted by the CLI. For PyTorch, 1 retains every epoch checkpoint and 0 retains only the best model. Due to a known TensorFlow limitation, both TensorFlow CLI values currently retain intermediate model directories.

``-M``
   The number of ensemble models. It is recommended to use 5. Default value is 5.

``--backend``
   Training backend: ``tensorflow`` (default) or ``pytorch``. TensorFlow training requires Python 3.8-3.9. PyTorch models must be predicted with the PyTorch backend.

``--device``
   PyTorch device. The default is ``cuda``; examples include ``cuda:1``, ``cpu``, and ``auto``. A requested CUDA device must be available and DASDC does not silently fall back to CPU.

``--epochs`` / ``--batch-size`` / ``--learning-rate``
   PyTorch training controls. Defaults are 50, 32, and 0.01, respectively.

``--patience`` / ``--seed`` / ``--workers``
   PyTorch early-stopping patience, random seed, and DataLoader worker count. Defaults are 5, 42, and 0.

``--amp`` / ``--no-amp``
   Enable or disable PyTorch CUDA automatic mixed precision. AMP is enabled by default and ignored on CPU.

**Demo:** Input the training, validation, testing datasets and labels (all generated in Step 4), and the real data feature matrix (generated in Step 3). Output the trained model to the ``Ensemble_CEU`` folder.

.. code-block:: shell

   dasdc train \
       --train-data trainSet/trainSet.npy \
       --train-label trainSet/trainSet_label.npy \
       --valid-data trainSet/validSet.npy \
       --valid-label trainSet/validSet_label.npy \
       --test-data trainSet/testSet.npy \
       --test-label trainSet/testSet_label.npy \
       -t real_feature/ \
       -o ../Ensemble_CEU

For PyTorch GPU training, append the backend and device options:

.. code-block:: shell

   dasdc train \
       --train-data trainSet/trainSet.npy \
       --train-label trainSet/trainSet_label.npy \
       --valid-data trainSet/validSet.npy \
       --valid-label trainSet/validSet_label.npy \
       --test-data trainSet/testSet.npy \
       --test-label trainSet/testSet_label.npy \
       -t real_feature/ -M 5 \
       -o ../Ensemble_CEU \
       --backend pytorch --device cuda

PyTorch checkpoints are stored under ``../Ensemble_CEU_ensemble/model_N/model.pt`` together with a tab-separated training log. The ensemble directory also contains ``ensemble.json`` with the input shape, backend, PyTorch version, and validation/test metrics.

-----------------------------------------------------------------------
Step 6: Prediction
-----------------------------------------------------------------------

Use ``pred`` to output selective sweep detection and classification results.

**Parameter description:**

``-m`` or ``--model``
   Path of folder which contains the sub-models used for ensemble.

``-M``
   Required number of ensemble models. TensorFlow prediction currently requires ``-M 5``. PyTorch prediction accepts another ensemble count, but the model directory must contain exactly the requested number of ``model.pt`` checkpoints. There is no CLI default.

``-f`` or ``--feature``
   Path of the feature matrix for the data to be predicted (the output of Step 3, ending with ``vcf_featureMap.npy``).

``-p`` or ``--position``
   Path of the position information for the data to be predicted (the output of Step 3, ending with ``vcfposInfo``).

``-o`` or ``--out``
   Path of pred result.

``--backend``
   Prediction backend: ``tensorflow`` (default) or ``pytorch``. It must match the backend used for training.

``--device`` / ``--batch-size``
   PyTorch prediction device and batch size. Defaults are ``cuda`` and 256.

**Demo:** Perform prediction on ``CEU.chr2.vcf_featureMap.npy`` (Chromosome 2 of CEU population).

.. code-block:: shell

   dasdc pred \
       -m ../Ensemble_CEU_ensemble/ \
       -M 5 \
       -f real_feature/CEU.chr2.vcf_featureMap.npy \
       -p real_feature/CEU.chr2.vcfposInfo \
       -o pred_res/CEU.chr2.pred.txt

For a PyTorch ensemble, append ``--backend pytorch --device cuda`` to the prediction command.

``../Ensemble_CEU_ensemble/`` is the path of folder which contains multi sub-models; the value after ``-M`` corresponds to the number of models the folder contains. ``real_feature/CEU.chr2.vcf_featureMap.npy`` and ``real_feature/CEU.chr2.vcfposInfo`` are the outputs of Step 3, which are the feature and position information for a single chromosome respectively.

.. important::

   For whole-genome prediction, each chromosome needs to be predicted separately. If you have ten chromosomes to predict, you need to execute Step 6 ten times.

-----------------------------------------------------------------------
Output
-----------------------------------------------------------------------

Output File Description
=======================

Taking the output results of ``CEU.chr2.vcf_featureMap.npy`` as an example:

.. figure:: https://github.com/soo-h/DASweepDetect/assets/74720083/dfe357d9-7e9f-4474-9686-5078228cb314
   :alt: Output file example
   :align: center

   Output file example

The first column represents the left endpoint of the predicted region. The second column represents the right endpoint of the predicted region. The third column represents the classification type. The fourth column represents the predicted probability. The fifth column represents the probability of being predicted for each of the five categories.

Taking the first row as an example, the region from 485 kbp to 535 kbp is determined to be neutral class (according to the label 4 in ``label_configure.txt``).

Filtering Prediction Results
============================

Retaining only the highest-scoring 5% of windows classified as soft sweeps is recommended to prioritize exploratory candidates. This stricter filtering is motivated by the greater heterogeneity and weaker separability of soft-sweep signals compared with hard-sweep signals. Population history, recombination-rate heterogeneity, missing genomic regions, and simulation-to-real domain mismatch can further cause neutral or other classes to be predicted as soft sweeps or soft linkage, leading to a higher false-positive rate.

For visualization, hard-sweep and hard-linkage scores may be combined to increase detection power at the cost of precision. Soft-sweep and soft-linkage scores should not be combined because neutral and other classes are more likely to be misclassified as soft linkage; combining the scores would carry these false-positive signals into the reported soft-sweep candidates.

-----------------------------------------------------------------------
Available Models
-----------------------------------------------------------------------

We put some models trained for specific species (or populations) at `Mendeley Data <https://data.mendeley.com/datasets/vdg2nbpc4j>`_. Users can directly select the model corresponding to the population to be studied for the detection and classification of the selective sweep.

**This process is done in the following two steps:**

- **Step 1:** Feature engineering for real genomic data (details see Step 3 in Usage).
  The input is a folder which constitutes of only single-chromosome VCF format files. If genome-wide data is used, it needs to be split into multiple files by chromosome.

- **Step 2:** Prediction (details see Step 6 in Usage).
  Make predictions about the feature of one chromosome. To predict genome-wide data, it needs to predict chromosome features separately.

**Demo:**

Step 1: Get real feature matrix.

.. code-block:: shell

   dasdc calc_target -i real_data -o real_feature

``real_data`` is a folder which contains input data with **VCF** format; ``real_feature`` is an output folder which contains output features of the input VCF file, and one chromosome corresponds to one output feature file.

Step 2: Get predict result.

.. code-block:: shell

   dasdc pred \
       -m MODEL_PATH \
       -M 5 \
       -f real_feature/CEU.chr2.vcf_featureMap.npy \
       -p real_feature/CEU.chr2.vcfposInfo \
       -o pred_res/CEU.chr2.pred.txt

``MODEL_PATH`` is the path of folder which contains multi sub-models. The value after ``-M`` corresponds to the number of models the folder contains. ``real_feature/CEU.chr2.vcf_featureMap.npy`` and ``real_feature/CEU.chr2.vcfposInfo`` are the outputs of Step 1, which are the feature and position information for a single chromosome respectively.

.. important::

   For whole-genome prediction, each chromosome needs to be predicted separately. If you have ten chromosomes to predict, you need to execute Step 2 ten times.

Homo sapiens
============

CEU Model
---------

**Description:** Model for detection and classification of selective sweeps in Utah residents with Northern and Western European ancestry population.

**Location:** ``available_models/Homo_sapiens/CEU``

Sus scrofa domestica
====================

LW Model
--------

**Description:** Model for detection and classification of selective sweeps in Large White pig population.

**Location:** ``available_models/Sus_scrofa/LW``

Anopheles gambiae
=================

BFS Model
---------

**Description:** Model for detection and classification of selective sweeps in *A. gambiae* from Burkina Faso population.

**Location:** ``available_models/Anopheles_gambiae/BFS``

-----------------------------------------------------------------------
FAQ
-----------------------------------------------------------------------

Report problems through the `GitHub issue tracker <https://github.com/soo-h/DASweepDetect/issues>`_. The upstream project also lists DASDC Communication QQ Group: **602055867**.
