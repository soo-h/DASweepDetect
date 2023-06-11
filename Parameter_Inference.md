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



```shell
example.poplabels
```



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
		--sample example.input.sample.gz --map $map --memory $mem --annot example.input.annot \
		--seed 1 -o example
```

script represents the path to the binary file `Relate` required for this operation. N denotes the effective population size, which should be set based on the effective population size of the species. m represents the mutation rate, which should be set as a prior assumption. 'example.input.sample.gz', 'example.input.sample.gz', and 'example.input.annot' are the output results from 1.2.  'example' is the prefix for the resulting output, which will generate two files: 'example.anc' and 'example.mut'.



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

'PATH_TO_RELATE/bin/RelateMutationRate' represents the path to the binary file `RelateMutationRate` required for this operation. 'example' is the prefix for the files 'example.anc' and 'example.mut'. Use the '-years_per_gen' option to specify the generation time interval information. 'example_mutation' is the output file which contains estimated recombination rate information.

<2> Inference base on Multiple Chromosome

```shell
input=example
gen=2
star=1
end=9
script=PATH_TO_RELATE/bin/RelateMutationRate

bash $script -i $input \
             --first_chr $star --last_chr $end\
             --years_per_gen $gen \
             --seed 1 \
             -o example_mutation
```

'PATH_TO_RELATE/bin/RelateMutationRate' represents the path to the binary file `RelateMutationRate` required for this operation. 'example' is the prefix for the files 'example.anc' and 'example.mut'. 'star 'is the starting chromosome number used for inference. 'end' is the ending chromosome number used for inference. Use the '-years_per_gen' option to specify the generation time interval information. 'example_mutation' is the output file which contains estimated recombination rate information.



### Step3. Demographic Inference

**Recommendation: Joint Inference using Multiple Chromosomes**

<1> Inference base on Single Chromosome

```shell
script=PATH_TO_RELATE/scripts/EstimatePopulationSize/EstimatePopulationSize.sh
gen=2
thread=5
bash $script -i example \
             -m 1.25e-8 \
             -years_per_gen $gen \
             --threads $thread \
             --poplabels example.poplabels \
             --seed 1 \
             -o example_popsize
```

'PATH_TO_RELATE/scripts/EstimatePopulationSize/EstimatePopulationSize.sh' represents the path to the script file `EstimatePopulationSize.sh` required for this operation. 'example' is the prefix for the files 'example.anc' and 'example.mut'. Use the '-years_per_gen' option to specify the generation time interval information. 'example.poplabels' is the file generated in step 1.2 <1>. 'thread' is the number of thread used for this progress. 'example_popsize' is the output file which contains estimated demographic information.



<2> Inference base on Multiple Chromosome

```shell
input=LW #Set a common prefix for multiple chromosomes
poplab=example.poplabels
gen=2
thread=5
star=1
end=9
script=/public/hsong/software/parameter_inference/relate_v1.1.8_x86_64_dynamic/scripts/EstimatePopulationSize/EstimatePopulationSize.sh 

bash $script -i $input \
             --first_chr $star --last_chr $end\
             -m 1.25e-8 \
             --poplabels example.poplabels \
             --years_per_gen $gen \
             --threads $thread\
             --seed 1 \
             -o example_popsize
```

'PATH_TO_RELATE/scripts/EstimatePopulationSize/EstimatePopulationSize.sh' represents the path to the script file `EstimatePopulationSize.sh` required for this operation. 'example' is the prefix for the files 'example.anc' and 'example.mut'. 'star 'is the starting chromosome number used for inference. 'end' is the ending chromosome number used for inference.  Use the '-years_per_gen' option to specify the generation time interval information. 'example.poplabels' is the file generated in step 1.2 <1>. 'thread' is the number of thread used for this progress. 'example_popsize' is the output file which contains estimated demographic information.

## Prior Setting for Selection Strength

Selection strength is anchored through prior assumptions, with a recommended range spanning two orders of magnitude. For populations under weak selection,such as Humans. It is recommended to use：**0.0001* 2N,0.01*2N**(N is the effective population size)

For populations under strong selection, such as Mosquitoes, Domestic Pigs. It is recommended to use: **0.001* 2N,0.1*2N**(N is the effective population size)



## Inference or Prior Setting of Recombination Rate

The lower limit of recombination rate is recommended to be the mean of inferred mutation rate, and the upper limit of recombination rate is recommended to be three times of the mean of inferred mutation rate. 