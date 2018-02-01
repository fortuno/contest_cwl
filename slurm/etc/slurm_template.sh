#!/usr/bin/env bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --workdir=XX_SCRATCH_DIR_XX
#SBATCH --cpus-per-task=XX_CORE_COUNT_XX
#SBATCH --mem=XX_MEM_XX
#SBATCH --gres=SCRATCH:XX_DISK_GB_XX

##ENV VARIABLE
SCRATCH_DIR="XX_SCRATCH_DIR_XX"
REPO_HASH="XX_REPO_HASH_XX"

##JOB VARIABLE
CWL_WORKFLOW="XX_CWL_WORKFLOW_XX"
CASE_ID="XX_CASE_ID_XX"
TUMOR_INPUT_GDC_ID="XX_TUMOR_BAM_GDC_ID_XX"
TUMOR_INPUT_S3URL="XX_TUMOR_BAM_S3URL_XX"

S3_LOAD_BUCKET="XX_LOAD_BUCKET_XX"
OUTPUT_UUID="XX_UUID_XX"
NTHREADS="XX_CORE_COUNT_XX"

function cleanup (){
    echo "cleanup tmp data";
    sudo rm -rf ${job_dir};
}

function main()
{

    local scratch_dir=${SCRATCH_DIR}
    local repository=${REPO_HASH}

    job_dir=`sudo mktemp -d pindel.XXXXXXXXXX -p $scratch_dir`
    sudo chown ubuntu:ubuntu ${job_dir}

    cd ${job_dir}
    
    sudo git clone -b feat/slurm ${repository}
    sudo chown ubuntu:ubuntu -R ${repository}

    trap cleanup EXIT
    
    local load_bucket=${S3_LOAD_BUCKET}   
    local json_template=${job_dir}/${repository}/slurm/etc/job_template.json
    local cwl_runner=${job_dir}/${repository}/workflow/${CWL_WORKFLOW}
    local db_config=/mnt/reference/fortuno_postgres_config

    /home/ubuntu/.virtualenvs/p2/bin/python ${repository}/slurm/contest-run-workflow.py run_cwl \
    --case_id ${CASE_ID} \
    --tumor_id ${TUMOR_INPUT_GDC_ID} \
    --tumor_s3url ${TUMOR_INPUT_S3URL} \
    --output_uuid ${OUTPUT_UUID} \
    --s3_load_bucket ${load_bucket} \
    --json_template ${json_template} \
    --basedir ${job_dir} \
    --cwl_runner ${cwl_runner} \
    --db_config ${db_config} 
    
}

main "$@"
