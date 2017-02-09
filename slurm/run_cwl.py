import argparse
import os
import sys
import setupLog
import logging
import tempfile
import time
import datetime
import pipelineUtil
#from elapsed_time import Time as Time
#import postgres
#import status_postgres

def parseOptions():

    parser = argparse.ArgumentParser(description="Run ContEst workflow CWL")

    # Logging arguments
    parser.add_argument('--debug',
        action = 'store_const',
        const = logging.DEBUG,
        dest = 'level',
        help = 'Enable debug logging.',
    )
    parser.set_defaults(level = logging.INFO)

    required = parser.add_argument_group("Required input parameters")
    required.add_argument("--normal_signpost_id", required=True, help="signpost ID for normal bam file")
    required.add_argument("--tumor_signpost_id", required=True, help="signpost ID for tumor bam file")
    required.add_argument("--ref_dict_signpost_id", required=True, help="signpost ID for reference dict file")
    required.add_argument("--ref_fa_signpost_id", required=True, help="signpost ID for reference file")
    required.add_argument("--ref_fai_signpost_id", required=True, help="signpost ID for reference index file")            
    required.add_argument("--tumor_case_id", required=True, help="Tumor Case ID")    
    required.add_argument("--aws_config", required=True, help="AWS config file")     
    required.add_argument("--aws_shared_credentials", required=True, help="AWS Shared credentials")
    required.add_argument("--endpoint_json", required=True, help="Endpoint json file")
    required.add_argument("--popfile_signpost_id", required=True, help="Population json file")   
    required.add_argument("--popfile_tbi_signpost_id", required=True, help="Population json index file")    
    required.add_argument("--cwl", required=True, help="Path to CWL code")
    required.add_argument("--signpost_base_url", required=True, help="signpost base url")
    required.add_argument("--s3dir", default="s3://bioinformatics_scratch/fortuno", help="path to output files")
    
    optional = parser.add_argument_group("Optional input parameters")
    optional.add_argument("--lane_level_contamination", default="SAMPLE", help="contamination level calculation")
    optional.add_argument("--population", default="ALL", help="population to obtain allele frequency")    
    optional.add_argument("--s3section", default="cleversafe", help="path to output files")
    optional.add_argument("--basedir", default="/mnt/SCRATCH/", help="Base directory for computations")

    args = parser.parse_args() 

    return args   

def is_nat(x):
    '''
    Checks that a value is a natural number.
    '''
    if int(x) > 0:
        return int(x)
    raise argparse.ArgumentTypeError('%s must be positive, non-zero' % x)

if __name__ == "__main__":

    args = parseOptions()

    if not os.path.isdir(args.basedir):
        raise Exception("Could not find path to base directory: %s" %args.basedir)

    #create directory structure
    casedir = tempfile.mkdtemp(prefix="contest_%s_" %args.tumor_case_id, dir=args.basedir)
    workdir = tempfile.mkdtemp(prefix="workdir_", dir=casedir)
    inp = tempfile.mkdtemp(prefix="input_", dir=casedir)
    print "Workdir: " + workdir
    print "Input: " + inp

    #setup logger
    log_file = os.path.join(workdir, "%s.contest.cwl.log" %str(args.tumor_case_id))
    logger = setupLog.setup_logging(logging.INFO, str(args.tumor_case_id), log_file)

    #logging inputs
    logger.info("normal_bam_id: %s" %(args.normal_signpost_id))
    logger.info("tumor_bam_id: %s" %(args.tumor_signpost_id))
    logger.info("tumor_case_id: %s" %(args.tumor_case_id))

    #Get datetime
    datetime_now = str(datetime.datetime.now())
    #Get CWL start time
    cwl_start = time.time()


    os.chdir(workdir)
    #run cwl command
    cwltool_path = '/home/ubuntu/.virtualenvs/jhs_cwl/bin/cwltool'
    cmd = [cwltool_path,
            "--debug",
            "--tmpdir-prefix", inp,
            "--tmp-outdir-prefix", workdir,
            args.cwl,
            "--tumor_bam_signpost_id", args.tumor_signpost_id,
            "--normal_bam_signpost_id", args.normal_signpost_id,
            "--reference_fa_signpost_id", args.ref_fa_signpost_id,
            "--reference_fai_signpost_id", args.ref_fai_signpost_id,
            "--reference_dict_signpost_id", args.ref_dict_signpost_id,
            "--signpost_base_url", args.signpost_base_url,            
            "--aws_config", args.aws_config,
            "--aws_shared_credentials", args.aws_shared_credentials,
            "--endpoint_json", args.endpoint_json,            
            "--popfile_signpost_id", args.popfile_signpost_id,
            "--popfile_tbi_signpost_id", args.popfile_tbi_signpost_id,            
            "--population", args.population,
            "--lane_level_contamination", args.lane_level_contamination,
            "--tumor_case_id", args.tumor_case_id,
            "--load_bucket", args.s3dir,
            "--s3cfg_section", args.s3section]
    
    print "Running " + ' '.join(cmd)
    cwl_exit = pipelineUtil.run_command(cmd, logger)

    cwl_failure = False
    if cwl_exit:
        cwl_failure = True
        print "Has failed"

    # upload logs to s3
    remote_path = args.s3dir + '/' + args.tumor_case_id + '/'
    exit = pipelineUtil.upload_to_cleversafe(logger, cwltool_path, remote_path, log_file, args.aws_config, args.aws_shared_credentials, args.endpoint_json, args.s3section)
 
    #exit = pipelineUtil.upload_to_cleversafe(logger, cwl_tool_path, args.s3dir, log_file, args.s3section, "http://gdc-objstore.osdc.io/")

    cwl_end = time.time()
    cwl_elapsed = cwl_end - cwl_start
