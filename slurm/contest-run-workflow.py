#!/usr/bin/env python
import postgres.utils
import postgres.status
import postgres.mixins
import utils.pipeline
import tempfile
import datetime
import socket
import time
import argparse
import logging
import math
import os
import sys
import uuid

def run_build_slurm_scripts(args):

    # Slurm template and output path
    slurm_script_path   = args.slurm_script_path
    slurm_template_path = args.slurm_template_path
    cwl_runner          = args.cwl_runner

    # Node configuration
    repo_hash      = args.repo_hash
    s3_load_bucket = args.s3_load_bucket

    # Slurm resources and configuration
    resource_core_count   = args.resource_core_count
    resource_disk_bytes   = args.resource_disk_bytes
    resource_memory_bytes = args.resource_memory_bytes
    scratch_dir           = args.scratch_dir
    
    # Postgres configuration
    input_table_name = args.input_table_name
    postgres_config  = args.postgres_config

    # Get list of cases from input table
    engine = postgres.utils.get_db_engine(postgres_config)
    cases = postgres.status.get_tn_cases(engine, input_table_name)
    
    for case in cases:    

        output_uuid = str(uuid.uuid4())

        case_id = case.case_id
        tumor_case   = case.tumor_bam_uuid
        tumor_s3url  = case.tumor_bam_location
    
        job_slurm = os.path.join(slurm_script_path, output_uuid + ".sh")
        f_open = open(job_slurm, 'w')
        with open(args.slurm_template_path, 'r') as read_open:
            for line in read_open:
                if 'XX_TUMOR_BAM_GDC_ID_XX' in line:
                    newline = line.replace('XX_TUMOR_BAM_GDC_ID_XX', tumor_case)
                    f_open.write(newline)
                elif 'XX_CASE_ID_XX' in line:
                    newline = line.replace('XX_CASE_ID_XX', case_id)
                    f_open.write(newline)
                elif 'XX_TUMOR_BAM_S3URL_XX' in line:
                    newline = line.replace('XX_TUMOR_BAM_S3URL_XX', tumor_s3url)
                    f_open.write(newline)                                 
                elif 'XX_REPO_HASH_XX' in line:
                    newline = line.replace('XX_REPO_HASH_XX', repo_hash)
                    f_open.write(newline)
                elif 'XX_CORE_COUNT_XX' in line:
                    newline = line.replace('XX_CORE_COUNT_XX', str(resource_core_count))
                    f_open.write(newline)
                elif 'XX_MEM_XX' in line:
                    memory_mebibytes = int(math.ceil(resource_memory_bytes / 1024 / 1024))
                    newline = line.replace('XX_MEM_XX', str(memory_mebibytes))
                    f_open.write(newline)
                elif 'XX_DISK_GB_XX' in line:
                    disk_mebibytes = int(math.ceil(resource_disk_bytes / 1024 / 1024))
                    newline = line.replace('XX_DISK_GB_XX', str(disk_mebibytes))
                    f_open.write(newline)
                elif 'XX_SCRATCH_DIR_XX' in line:
                    newline = line.replace('XX_SCRATCH_DIR_XX', scratch_dir)
                    f_open.write(newline)
                elif 'XX_CWL_WORKFLOW_XX' in line:
                    newline = line.replace('XX_CWL_WORKFLOW_XX', cwl_runner)
                    f_open.write(newline)
                elif 'XX_LOAD_BUCKET_XX' in line:
                    newline = line.replace('XX_LOAD_BUCKET_XX', s3_load_bucket)
                    f_open.write(newline)   
                elif 'XX_UUID_XX' in line:
                    newline = line.replace('XX_UUID_XX', output_uuid)
                    f_open.write(newline)                                                         
                else:
                    f_open.write(line)
        f_open.close()


def run_build_json_input(args):

    tumor_url      = args.tumor_s3url
    tumor_uuid     = args.tumor_uuid
    output_uuid    = args.output_uuid
    s3_load_bucket = args.s3_load_bucket
    job_json       = args.json_input

    output_file = output_uuid + '_contamination.txt'
    f_open = open(job_json, 'w')
    with open(args.json_template, 'r') as read_open:
        for line in read_open:
            if 'XX_TUMOR_S3_PATH_XX' in line:
                newline = line.replace('XX_TUMOR_S3_PATH_XX', tumor_url)
                f_open.write(newline)
            elif 'XX_TUMOR_UUID_XX' in line:
                newline = line.replace('XX_TUMOR_UUID_XX', tumor_uuid)
                f_open.write(newline)                
            elif 'XX_LOAD_BUCKET_XX' in line:
                newline = line.replace('XX_LOAD_BUCKET_XX', s3_load_bucket)
                f_open.write(newline)              
            else:
                f_open.write(line)
    f_open.close()

    return job_json

def run_cwl(args, json_file):

    output_uuid = args.output_uuid
    case_id = args.case_id
    tumor_id = args.tumor_id
    cwl_version = args.cwl_version
    docker_version = [args.docker_version]

    #create directory structure
    casedir = tempfile.mkdtemp(prefix="case_%s" % output_uuid, dir=args.basedir)
    workdir = tempfile.mkdtemp(prefix="workdir_%s" % output_uuid, dir=casedir)
    inp     = tempfile.mkdtemp(prefix="input_%s" % output_uuid, dir=casedir)

    #generate a random uuid
    output_file = "%s_contamination.txt" % (str(output_uuid))

    # get hostname and datetime
    hostname = socket.gethostname()
    datetime_start = str(datetime.datetime.now())

    #setup logger
    log_file = os.path.join(workdir, "%s.contest.cwl.log" % str(output_uuid))
    logger = utils.pipeline.setup_logging(output_uuid, log_file)

    #logging inputs
    logger.info("bam_tumor_id: %s" %(args.tumor_id))   
    logger.info("output: %s" %(str(output_file)))
    logger.info("hostname: %s" % (hostname))    
    logger.info("datetime_start: %s" % (datetime_start))

    #Get CWL start time
    cwl_start = time.time()

    # Run CWL
    os.chdir(workdir)
    logger.info('Running CWL workflow')
    cmd = ['/usr/bin/time', '-v',
           '/home/ubuntu/.virtualenvs/p2/bin/cwltool',
           "--debug",
           "--tmpdir-prefix", inp,
           "--tmp-outdir-prefix", workdir,
           args.cwl_runner,
           json_file]
    cwl_exit = utils.pipeline.run_command(cmd, logger)
    cwl_failure = False
    if cwl_exit:
        cwl_failure = True

    # Get output md5sum
    output_full_path = os.path.join(workdir, output_file)
    md5 = utils.pipeline.get_md5(output_full_path)
    file_size = utils.pipeline.get_file_size(output_full_path)

    # Establish connection with database
    engine = postgres.utils.get_db_engine(args.db_config)

    # Calculate times
    cwl_end = time.time()
    cwl_elapsed = cwl_end - cwl_start
    datetime_end = str(datetime.datetime.now())
    logger.info("datetime_end: %s" % (datetime_end))

    # Get status info
    logger.info("Get status/metrics info")
    upload_dir_location = args.s3_load_bucket
    upload_file_location = os.path.join(upload_dir_location, output_file)
    status, loc = postgres.status.get_status(0, cwl_exit, upload_file_location, upload_dir_location, logger)
    
    # Get metrics info
    time_metrics = utils.pipeline.get_time_metrics(log_file)
    
    # Set status table
    logger.info("Updating status: %d" % cwl_exit)
    postgres.utils.add_pipeline_status(engine, output_uuid, tumor_id, case_id, status, 
                                       loc, datetime_start, datetime_end, md5,   
                                       file_size, hostname, cwl_version, docker_version, statusclass, logger)
    
    # Set metrics table
    logger.info("Updating metrics")
    postgres.utils.add_pipeline_metrics(engine, output_id, [args.input_id], args.input_table, download_time,
                                        upload_time, args.thread_count, cwl_elapsed,
                                        time_metrics['system_time'],
                                        time_metrics['user_time'],
                                        time_metrics['wall_clock'],
                                        time_metrics['percent_of_cpu'],
                                        time_metrics['maximum_resident_set_size'],
                                        status, metricsclass)
    
    # Remove job directories, upload final log file
    logger.info("Uploading main log file")
    #utils.s3.aws_s3_put(logger, upload_dir_location + '/' + os.path.basename(log_file), log_file, args.s3_profile, args.s3_endpoint, recursive=False)
    #utils.pipeline.remove_dir(jobdir)


def get_args():

    parser = argparse.ArgumentParser('GDC-contest-cwl-workflow')
    
    # Sub parser 
    sp = parser.add_subparsers(help='Choose the process you want to run', dest='choice')

    # Build slurm scripts
    p_slurm = sp.add_parser('slurm', help='Options for building slurm scripts.')    
    p_slurm.add_argument('--input_table_name', required = True)
    p_slurm.add_argument('--slurm_script_path', required = True)    
    p_slurm.add_argument('--repo_hash', required = True)
    p_slurm.add_argument('--resource_core_count',type = int,required = True)
    p_slurm.add_argument('--resource_disk_bytes',type = int,required = True)
    p_slurm.add_argument('--resource_memory_bytes',type = int,required = True)
    p_slurm.add_argument('--scratch_dir',required = True)
    p_slurm.add_argument('--slurm_template_path',required = True)  
    p_slurm.add_argument('--postgres_config',required = True) 
    p_slurm.add_argument('--s3_load_bucket',required = True)    
    p_slurm.add_argument('--cwl_runner',required = True) 

    # Build json files and run cwl
    p_input = sp.add_parser('run_cwl', help='Options for building input json and run cwl.')
    p_input.add_argument('--case_id', required = True)
    p_input.add_argument('--tumor_id', required = True)
    p_input.add_argument('--tumor_s3url', required = True) 
    p_input.add_argument('--output_uuid', required = True)    
    p_input.add_argument('--s3_load_bucket', required = True)
    p_input.add_argument('--json_template', default = 'job_template.json')
    p_input.add_argument('--basedir', required = True)
    p_input.add_argument('--cwl_runner',required = True) 
    p_input.add_argument('--db_config',required = True) 
    p_input.add_argument('--cwl_version', default="1.0.20170828135420",required = False) 
    p_input.add_argument('--docker_version', default="broadinstitute/gatk:latest",required = False) 

    return parser.parse_args() 


if __name__ == '__main__':
    
    # Get args
    args = get_args()

    # Run tool 
    if args.choice == 'slurm': 
        run_build_slurm_scripts(args)
    
    elif args.choice == 'run_cwl': 
        
        json_file = run_build_json_input(args)
        
        # Setup postgres classes for tables
        class TableStatus(postgres.mixins.StatusTypeMixin, postgres.utils.Base):
            __tablename__ = 'contest_cwl_status'
        class TableMetrics(postgres.mixins.MetricsTypeMixin, postgres.utils.Base):
            __tablename__ = 'contest_cwl_metrics'
        
        run_cwl(args, json_file)
