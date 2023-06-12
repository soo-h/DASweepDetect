# Instruction

**Required parameters: mutation rate, recombination rate, selection strength, demographic**

It is recommended to set these parameters based on previous relevant research findings. You can try to find useful information in `stdpopsim`.

[GitHub - popsim-consortium/stdpopsim: A library of standard population genetic models](https://github.com/popsim-consortium/stdpopsim)

If you cannot find the relevant parameters in previous research, it is recommended to combine prior knowledge and parameter inference to set the parameters.





# Mutation Rate and Demographic Inference

**Note: We use the Relate software for this**, as it provides fast computation and is suitable for parameter inference with large samples.

The inference process can be completed by following these steps：

- Step 1: Input file preparation
  - 1.1 Convert VCF data to SHAPEIT2 input format.
  - 1.2 Input file preparation is completed.
  - 1.3 Generate files for parameter inference.
- Step 2: Mutation rate inference.
- Step 3: Demographic inference.




### Step 1: Input File Preparation

#### 1.1 Convert VCF Data to SHAPEIT2 Input Format.

```shell
 PATH_TO_RELATE/bin/RelateFileFormats \
                 --mode ConvertFromVcf \
                 --haps example.haps \
                 --sample example.sample \
                 -i example 
```

Set `PATH_TO_RELATE` as the path where the Relate software is located. `RelateFileFormats` refers to the binary program used in this step. 'example' represents the input VCF file composed of a single chromosome, while 'example.haps' and 'example.sample' are the output files in SHAPEIT2 format.



#### 1.2 Input Files Preparation is Completed

<1>Generation of `poplabels` Files

Perform the following steps to generate `poplabels` files:

write this code in `get_poplabels.sh`

```shell
for ((i=1; i<=$1; i++)); do
    echo "1 group1 group1 0" >> example.poplabels
done
```

 <p align="center"><b>（script name: get_poplabels.sh  ）</b></p>

Execute `get_poplabels.sh` with the following command:

```shell
bash get_poplabels.sh sampleNum
```

sampleNum is the sample number in the vcf file



<2>Preparation of Input Files

```shell
ancestor=Sus_scrofa.Sscrofa11.1.dna.toplevel.fa # Ancestral reference sequence
script=PATH_TO_RELATE/scripts/PrepareInputFiles/PrepareInputFiles.sh # Use the PrepareInputFiles.sh script from Relate to complete the process

bash $script --haps example.haps \
            --sample example.sample \
            --poplabels example.poplabels \
            --ancestor $ancestor -o example.input 
```

ancestor refers to the reference sequence of the pig genome (Sus_scrofa.Sscrofa11.1.dna.toplevel.fa). Please download the corresponding reference sequence for the inferred species. 'Script' represents the path to the script `PrepareInputFiles.sh` required for this operation. 'example.haps' and 'example.sample' are the output files from step 1.1. 'example.poplabels' is the file generated in step 1.2 <1>. 'example.input' is the resulting output, which will generate three files: 'example.input.haps.gz', 'example.input.sample.gz', and 'example.input.annot'."



#### 1.3 Generate Files for Parameter Inference

<1> Generation of Genetic Map 

If the genetic map positions of the species are available, it is recommended to construct a genetic map based on the standard conversion of 1M equals 1CM.

<2> Generation of Files for Parameter Inference

```shell
script=PATH_TO_RELATE/bin/Relate
N=150
m=1.25e-8
mem=1
$script --mode All -m $m -N $N --haps example.input.haps.gz \
		--sample example.input.sample.gz --map $map --memory $mem \
		--annot example.input.annot \
		--seed 1 -o example
```

script represents the path to the binary file `Relate` required for this operation. N denotes the effective population size, which should be set based on the effective population size of the species. m represents the mutation rate, which should be set as a prior assumption. 'example.input.sample.gz', 'example.input.sample.gz', and 'example.input.annot' are the output results from 1.2.  'example' is the prefix for the resulting output, which will generate two files: 'example.anc' and 'example.mut'.

**Note: The input file should be located in the current path **



#### pipline for step1

This pipline is uesd to our previous study which integration 1.1, 1.2, and 1.3 , can directory get .anc and .mut file for mutation and demographic inference. 

**pipline1: input vcf file of single chromosome, get  .anc and .mut files of the chromosome.**

```shell
#!/usr/bin/bash

N=150
m=1.25e-8
mem=1
ancestor=Sus_scrofa.Sscrofa11.1.dna.toplevel.fa #Ancestral reference sequence
script1=PATH_TO_RELATE/bin/RelateFileFormats #
script2=PATH_TO_RELATE/scripts/PrepareInputFiles/PrepareInputFiles.sh #Use the PrepareInputFiles.sh script from Relate to complete the process
script3=PATH_TO_RELATE/bin/Relate #

name=$1
sampleNum=$2

$script1 --mode ConvertFromVcf \
		 --haps $name.haps \
		 --sample $name.sample \
         -i $name 

for ((i=1; i<=sampleNum; i++)); do
    echo "1 group1 group1 0" >> example.poplabels
done

bash $script2 --haps $name.haps \
            --sample $name.sample \
            --poplabels $name.poplabels \
            --ancestor $ancestor -o $name.input   
            
$script --mode All -m $m -N $N --haps $name.input.haps.gz \
		--sample $name.input.sample.gz --map $map --memory $mem --annot $name.input.annot \
		--seed 1 -o $name
```

 <p align="center"><b>（pipline name: getInputFiles.sh ）</b></p>

write this code in `getInputFiles.sh`  and seven parameter should be set, include: effective population size **N**, prior mutation rate **m**, memory required for program operation **mem**, ancestral reference sequence **ancestor**, Absolute path where `RelateFileFormats` is located **script1**, Absolute path where `PrepareInputFiles.sh` is located **script2**, Absolute path where `Relate` is located **script3**. 

Execute `getInputFiles.sh` with the following command:

```shell
bash getInputFiles.sh LW_chr1.vcf sampleNum
```

LW_chr1.vcf is the input vcf file of single chromosome; sampleNum is the sample number in the vcf file.



**pipline2: get .anc and .mut files of the whole genome.**

```shell
dir=$1
for name in $(ls $dir)
do
 getInputFiles.sh name
done
```

 <p align="center"><b>（pipline name: batch_getInputFiles.sh ）</b></p>

write this code in `batch_getInputFiles.sh` 

Execute the pipline with the following command:

```
bash batch_getInputFiles.sh dirpath
```

dirpath is the input folder path, which contains the single chromosome vcf files to be entered.



### Step2. Mutation Rate Inference

**Recommendation: Joint Inference using Multiple Chromosomes**

<1> Inference base on  Single Chromosome

```shell
gen=2
script=PATH_TO_RELATE/bin/RelateMutationRate
$script \ 
		--mode Avg \
		-i example \
		-years_per_gen $gen \
		-o example_mutation
```

'PATH_TO_RELATE/bin/RelateMutationRate' represents the path to the binary file `RelateMutationRate` required for this operation. 'example' is the prefix for the files 'example.anc' and 'example.mut'.  '-years_per_gen' is a optional option which specify years per generation, Default: 28 .  'example_mutation' is the output file which contains estimated recombination rate information.

<2> Inference base on Multiple Chromosome

```shell
input=example
gen=2
star=1
end=2
script=PATH_TO_RELATE/bin/RelateMutationRate

bash $script -i $input \
             --first_chr $star --last_chr $end\
             --years_per_gen $gen \
             -o example_mutation
```

'PATH_TO_RELATE/bin/RelateMutationRate' represents the path to the binary file `RelateMutationRate` required for this operation. 

'example' is the common prefix of the input file. The input file should follow the following naming rules and contain two types: _prefix \_ chromosome index.anc_ and _prefix \_ chromosome index.mut_. In this command, two chromosomes 1 and 2 are combined for joint inference, then the input files should contain four files, named example\_chr1.anc, example\_chr1.mut, example\_chr2.anc, example\_chr2.mut.

 'star 'is the starting chromosome number used for inference. 'end' is the ending chromosome number used for inference. 

'-years_per_gen' is a optional option which specify years per generation, Default: 28 . 'example_mutation' is the output file which contains estimated mutation rate information.



### Step3. Demographic Inference

**Recommendation: Joint Inference using Multiple Chromosomes**

<1> Inference base on Single Chromosome

```shell
script=PATH_TO_RELATE/scripts/EstimatePopulationSize/EstimatePopulationSize.sh
input=example
mutation=1.25e-8
gen=2
thread=5
poplab=example.poplabels
output=example_popsize
bash $script -i $input \
             -m $mutation \
             -years_per_gen $gen \
             --threads $thread \
             --poplabels $poplab \
             --seed 1 \
             -o $output
```

'PATH_TO_RELATE/scripts/EstimatePopulationSize/EstimatePopulationSize.sh' represents the path to the script file `EstimatePopulationSize.sh` required for this operation. 'example' is the prefix for the files 'example.anc' and 'example.mut'. '-years_per_gen' is a optional option which specify years per generation, Default: 28 . 'example.poplabels' is the file generated in step 1.2 <1>. 'thread' is the number of thread used for this progress. 'example_popsize' is the output file which contains estimated demographic.



<2> Inference base on Multiple Chromosome

```shell
script=PATH_TO_RELATE/scripts/EstimatePopulationSize/EstimatePopulationSize.sh
input=example #Set a common prefix for multiple chromosomes
poplab=example.poplabels
mutation=1.25e-8
gen=2
thread=5
star=1
end=2
output=example_popsize
bash $script -i $input \
             --first_chr $star --last_chr $end\
             -m $mutation \
             --poplabels $poplab \
             --years_per_gen $gen \
             --threads $thread\
             --seed 1 \
             -o $output
```

'PATH_TO_RELATE/scripts/EstimatePopulationSize/EstimatePopulationSize.sh' represents the path to the script file `EstimatePopulationSize.sh` required for this operation.

'example' is the common prefix of the input file. The input file should follow the following naming rules and contain two types: _prefix \_ chromosome index.anc_ and _prefix \_ chromosome index.mut_. In this command, two chromosomes 1 and 2 are combined for joint inference, then the input files should contain four files, named example\_chr1.anc, example\_chr1.mut, example\_chr2.anc, example\_chr2.mut.

 'star 'is the starting chromosome number used for inference. 'end' is the ending chromosome number used for inference.  '-years_per_gen' is a optional option which specify years per generation, Default: 28 . 'example.poplabels' is the file generated in step 1.2 <1>. 'thread' is the number of thread used for this progress. 'example_popsize' is the output file which contains estimated demographic.



## Prior Setting for Selection Strength

Selection strength is anchored through prior assumptions, with a recommended range spanning two orders of magnitude. For populations under weak selection,such as Humans. It is recommended to use：**0.0001* 2N,0.01*2N**(N is the effective population size)

For populations under strong selection, such as Mosquitoes, Domestic Pigs. It is recommended to use: **0.001* 2N,0.1*2N**(N is the effective population size)



## Inference or Prior Setting of Recombination Rate

The lower limit of recombination rate is recommended to be the mean of inferred mutation rate, and the upper limit of recombination rate is recommended to be three times of the mean of inferred mutation rate. 

