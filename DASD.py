# sourcery skip: avoid-builtin-shadow
import argparse
import subprocess
import sys
import os

DASDC_version = '1.0.1'

description_text = "\n".join([
    "==========================================================================",
    "DASDC: (D)omain (A)daptation (S)weep (D)etection and (C)lassification",
    "==========================================================================",
    f"Version: DASDC {DASDC_version}",
    "--------------------------------------------------------------------------",
])


class PreserveNewlinesHelpFormatter(argparse.ArgumentDefaultsHelpFormatter):
    def _fill_text(self, text, width, indent):
        # Split the text by "\n" and apply indentation to each paragraph
        return "".join(indent + line for line in text.splitlines(keepends=True))

# Program specification
parser = argparse.ArgumentParser(description=description_text,formatter_class=PreserveNewlinesHelpFormatter)

# -v output version information
parser.add_argument(
        '-v', '--version', action='version', version=f'DASDC v{DASDC_version}'
    )


# Build multiple Parsers to perform multiple steps. 
subparsers = parser.add_subparsers(help='sub-command help')
# Parser1：step1.simulation data
parser_simu = subparsers.add_parser('simu', help='step1:Simulate Data',description=\
'=============================================================================='
'\n|Note: this is complete by calling Discoal(doi:10.1093/bioinformatics/btw556)|'
'\n==============================================================================',formatter_class=PreserveNewlinesHelpFormatter)
parser_simu.add_argument('--config_file','-i',help='Path to the configure file')
parser_simu.add_argument('-o','--out',help='Output name of the simulation data')
parser_simu.set_defaults(func='simu')



# Parser2: simulation data feature engineering
parser_calc_simu = subparsers.add_parser('calc_domain', help='step2:Calcuate summary statistics to generate featureMap of simulation data')

parser_calc_simu.add_argument('-i ','--input',help='<string>: Path to the ms-style simulation data'\
    '\n When multiple files are entered, Please joint by ,'\
    '\n Example: file1,file2,file3')
parser_calc_simu.add_argument('--filter',help='Drop sample if SNP < the set value,default = 250', required=False, default=250)
parser_calc_simu.add_argument('--core', help='CPU Number,default=8,recommand n * 8,n is the number of input file', required=False, default=8)
parser_calc_simu.add_argument('-o ','--out',help='Path to the folder where featureMap to be stored')
parser_calc_simu.set_defaults(func='calc_domain')

# Parser3: real genome data feature engineering
parser_calc_target = subparsers.add_parser('calc_target', help='step3:Calcuate summary statistics to generate featureMap of target data(VCF Format)')
parser_calc_target.add_argument('-i ','--input',help='<string>: Path to the VCF or VCF.gz File'\
    '\n When multiple files are entered, Please joint by ,'\
    '\n Example: file1,file2,file3')
parser_calc_target.add_argument('--filter',help='Drop sample if SNP < the set value,default = 250', required=False, default=250)
parser_calc_target.add_argument('--core', help='CPU Number,default=8,recommand n * 8,n is the number of input file', required=False, default=6)
parser_calc_target.add_argument('--start', help='The starting point of the region to be calculated', required=False, default=None)
parser_calc_target.add_argument('--end', help='The end point of the region to be calculated', required=False, default=None)
parser_calc_target.add_argument('--window-size', help='The windows size of convert feature map', required=False, default=1000000)
parser_calc_target.add_argument('--window-step', help='The step of windows', required=False,default=None)
parser_calc_target.add_argument('-o ','--out',help='Path to the folder where featureMap to be stored')
parser_calc_target.set_defaults(func='calc_target')

# Parser4: data annotation
parser_data_annotation = subparsers.add_parser('data_annotation', help='step4:Annotation data by user-provided profile')
parser_data_annotation.add_argument('-i ','--input',help='<string>: Path to the VCF or VCF.gz File'\
    '\n When multiple files are entered, Please joint by ,'\
    '\n Example: file1,file2,file3')
parser_data_annotation.add_argument('--config', help='Path to the configure file')
parser_data_annotation.add_argument('-o ','--out',help='Path to the folder where dataset to be stored')
parser_data_annotation.set_defaults(func='data_annotation')

# Parser5：model training
parser_train = subparsers.add_parser('train',help="step5:Domain Adaptive Model Training")
parser_train.add_argument('--train-data',help='Path to the Train data')
parser_train.add_argument('--train-label',help='Path to the Train Label data')
parser_train.add_argument('--valid-data',help='Path to the Valid data')
parser_train.add_argument('--valid-label',help='Path to the Valid Label data')
parser_train.add_argument('--test-data',help='Path to the Valid data')
parser_train.add_argument('--test-label',help='Path to the Valid Label data')
parser_train.add_argument('-t','--target', help='Path to the feature map file(single or multi) / directory of target data'\
'\n multi file should joint by , ; directory should only include feature map file')
parser_train.add_argument('-M',help='Model number to train', required=False, default=5)
parser_train.add_argument('-s','--save',help='1 is save model generated during iteration and 0 is only save best model', required=False, default=0)
parser_train.add_argument('-o ','--out',help='Path to the model to be stored')
parser_train.set_defaults(func='train')
## Prser6：predict
parser_pred = subparsers.add_parser('pred',help="step6:Sweep Dectection And Classifition")
parser_pred.add_argument('-m','--model',help='Path to model')
parser_pred.add_argument('-M',help='Number of integrated models')
parser_pred.add_argument('-f','--feature',help='Path to feature map of target data')
parser_pred.add_argument('-p','--position',help='Path to position infomation of target data')
parser_pred.add_argument('-o','--out',help='Path to the result of output')
parser_pred.set_defaults(func='pred')



# Parsing parameters
args = parser.parse_args()

currend_work_dir = os.getcwd()
DASD_directory = os.path.dirname(os.path.abspath(__file__))

def convert_abs_path(realtive_path, cwd=currend_work_dir):
    abs_path = os.path.abspath(os.path.join(cwd, realtive_path))
    return abs_path

if 'func' in args:
    if args.func == 'simu':
        if args.config_file is None:
            parser_simu.print_help()
            sys.exit(1)
    
    
        configure_file = convert_abs_path(args.config_file)
        opt_file = convert_abs_path(args.out)
        script = convert_abs_path('DASD/simudata_gen.py',DASD_directory)
        discoal_path = convert_abs_path('discoal',DASD_directory)
        cmd_simu = f"python3.8 {script} {configure_file} {opt_file} {discoal_path}"
        subprocess.call(cmd_simu,shell=True)




    elif args.func == 'calc_domain':
        if args.input is None:
            parser_calc_simu.print_help()
            sys.exit(1)
        ipt = convert_abs_path(args.input)
        filter = args.filter
        core = args.core
        outdir = convert_abs_path(args.out)

        script = convert_abs_path('DASD/simudata_to_feature.py ', DASD_directory)

        cmd_calcsimu = f"python3.8 {script} {ipt} {core} {filter} {outdir}"
        subprocess.call(cmd_calcsimu,shell=True)


    elif args.func == 'calc_target':
        if args.input is None :
            parser_calc_target.print_help()
            sys.exit(1)
            
        ipt = convert_abs_path(args.input)
        core = args.core
        filter = args.filter
        start = args.start
        end = args.end
        size = args.window_size
        step = args.window_step
        outdir = convert_abs_path(args.out)

        script = convert_abs_path('DASD/vcf_to_featureMap.py ', DASD_directory)
        
        cmd_calcsimu = f"python3.8 {script} {ipt} {core} {filter} {start} {end} {size} {step} {outdir}"
        print(cmd_calcsimu)
        subprocess.call(cmd_calcsimu,shell=True)

    elif args.func == 'data_annotation':
        if args.input is None:
            parser_data_annotation.print_help()
            sys.exit(1)

        ipt = convert_abs_path(args.input)
        configure_file = convert_abs_path(args.config)
        outdir = convert_abs_path(args.out)

        script = convert_abs_path('DASD/label_data.py ', DASD_directory)

        cmd_simu = f"python3.8 {script} {ipt} {configure_file} {outdir}"
        subprocess.call(cmd_simu,shell=True)

    elif args.func == 'train':
        if args.train_data is None:
            parser_train.print_help()
            sys.exit(1)

        train_data = convert_abs_path(args.train_data)
        train_label = convert_abs_path(args.train_label)
        valid_data = convert_abs_path(args.valid_data)
        valid_label = convert_abs_path(args.valid_label)
        test_data = convert_abs_path(args.test_data)
        test_label = convert_abs_path(args.test_label)
        target = convert_abs_path(args.target)
        M = args.M
        save = args.save
        out = convert_abs_path(args.out)

        script = convert_abs_path('DASD/DANN_train.py ', DASD_directory)

        cmd_train = f"python3.8 {script} {train_data} {train_label} {valid_data} {valid_label} {test_data} {test_label} {target} {M} {save} {out}"
        subprocess.call(cmd_train,shell=True)

    elif args.func == 'pred':
        if args.model is None:
            parser_pred.print_help()
            sys.exit(1)
        
        model = convert_abs_path(args.model, DASD_directory)
        feature = convert_abs_path(args.feature,DASD_directory)
        position = convert_abs_path(args.position,DASD_directory)
        out = convert_abs_path(args.out)
        M = args.M

        script = convert_abs_path('DASD/pred_ensemble.py ', DASD_directory)

        cmd_pred = f"python3.8 {script} {model} {M} {feature} {position} {out}"
        subprocess.call(cmd_pred,shell=True)


else:
    parser.print_help()
