#!/bin/bash
#SBATCH --nodes=1
#SBATCH --cpus-per-task=XX_THREAD_COUNT_XX
#SBATCH --ntasks=1
#SBATCH --workdir="/mnt/SCRATCH/"
#SBATCH --mem=XX_MEM_XX

# java_heap="XX_JAVAHEAP_XX"

normal_id="XX_NORMAL_ID_XX"
tumor_id="XX_TUMOR_ID_XX"
ref_fa_id="XX_REF_FA_ID_XX"
ref_fai_id="XX_REF_FAI_ID_XX"
ref_dict_id="XX_REF_DICT_ID_XX"
popfile_json="XX_POPFILE_ID_XX"
popfile_tbi_json="XX_POPFILE_TBI_ID_XX"
case_id="XX_CASE_ID_XX"
s3dir="XX_S3DIR_XX"
base_url="XX_BASE_URL_XX"

aws_config=${HOME}/.aws/config
aws_creds=${HOME}/.aws/credentials
endpoint_json=${HOME}/endpoint.json

repository="git@github.com:fortuno/contest_cwl.git"
wkdir=`sudo mktemp -d contest.XXXXXXXXXX -p /mnt/SCRATCH/`
sudo chown ubuntu:ubuntu $wkdir

cd $wkdir

function cleanup (){
    echo "cleanup tmp data";
    sudo rm -rf $wkdir;
}

sudo git clone -b slurm $repository
sudo chown ubuntu:ubuntu -R contest_cwl

trap cleanup EXIT

/home/ubuntu/.virtualenvs/p2/bin/python $wkdir/contest_cwl/slurm/run_cwl.py \
--normal_signpost_id $normal_id \
--tumor_signpost_id $tumor_id \
--ref_dict_signpost_id $ref_dict_id \
--ref_fa_signpost_id $ref_fa_id \
--ref_fai_signpost_id $ref_fai_id \
--tumor_case_id $case_id \
--aws_config $aws_config \
--aws_shared_credentials $aws_creds \
--endpoint_json $endpoint_json \
--popfile_signpost_id $popfile_json \
--popfile_tbi_signpost_id $popfile_tbi_json \
--basedir $wkdir \
--signpost_base_url $base_url \
--s3dir $s3dir \
--cwl $wkdir/contest_cwl/workflows/contest-tool-workflow.cwl.yaml
