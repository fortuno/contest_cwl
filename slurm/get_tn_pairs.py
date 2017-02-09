import argparse
import os

if __name__ == "__main__":


    parser = argparse.ArgumentParser(description="ContEst contamination estimation")

    required = parser.add_argument_group("Required input parameters")
    required.add_argument("--input_table", default=None, help="path to reference file", required=True)
    required.add_argument("--ref_id", default=None, help="Signpost id to reference file", required=True)
    required.add_argument("--ref_index_id", default=None, help="Signpost id to reference index file", required=True)    
    required.add_argument("--ref_dict_id", default=None, help="Signpost id to reference dictionary file", required=True)
    required.add_argument("--aws_config", default=None, help="path to aws configuration file", required=True)
    required.add_argument("--aws_creds", default=None, help="path to aws shared credential file", required=True)
    required.add_argument("--endpoint_json", default=None, help="path to enpoint json file", required=True)     
    required.add_argument("--popfile_id", default=None, help="Signpost id to popfile json file", required=True) 
    required.add_argument("--popfile_tbi_id", default=None, help="Signpost id to popfile tbi json file", required=True)     
    required.add_argument("--signpost_base_url", default=None, help="path to output files", required=True)
    required.add_argument("--outdir", default="./", help="output directory for slurm scripts")  
    required.add_argument("--s3dir", default=None, help="path to output files", required=True)
    required.add_argument("--mem", default=None, help="mem for each node", required=True)
    required.add_argument("--thread_count", default=None, help="thread count", required=True)
    
    args = parser.parse_args()

    if not os.path.isdir(args.outdir):
        raise Exception("Cannot find output directory: %s" %args.outdir)

    with open(args.input_table, "r") as f:
        for input_line in f:
            columns = input_line.strip('\n').split('\t')
            slurm = open(os.path.join(args.outdir, "contest.%s.%s.sh" %(columns[5], columns[9])), "w")
            temp = open("template.sh", "r")
            for line in temp:

                if "XX_NORMAL_ID_XX" in line:
                    line = line.replace("XX_NORMAL_ID_XX", columns[5])

                if "XX_TUMOR_ID_XX" in line:
                    line = line.replace("XX_TUMOR_ID_XX", columns[9])

                if "XX_CASE_ID_XX" in line:
                    line = line.replace("XX_CASE_ID_XX", columns[2])

                if "XX_REF_FA_ID_XX" in line:
                    line = line.replace("XX_REF_FA_ID_XX", args.ref_id)

                if "XX_REF_FAI_ID_XX" in line:
                    line = line.replace("XX_REF_FAI_ID_XX", args.ref_index_id)

                if "XX_REF_DICT_ID_XX" in line:
                    line = line.replace("XX_REF_DICT_ID_XX", args.ref_dict_id)

                if "XX_AWS_CONFIG_XX" in line:
                    line = line.replace("XX_AWS_CONFIG_XX", args.aws_config)

                if "XX_AWS_CREDS_XX" in line:
                    line = line.replace("XX_AWS_CREDS_XX", args.aws_creds)

                if "XX_ENDP_JSON_XX" in line:
                    line = line.replace("XX_REF_DICT_ID_XX", args.endpoint_json)

                if "XX_POPFILE_ID_XX" in line:
                    line = line.replace("XX_POPFILE_ID_XX", args.popfile_id)

                if "XX_POPFILE_TBI_ID_XX" in line:
                    line = line.replace("XX_POPFILE_TBI_ID_XX", args.popfile_tbi_id)

                if "XX_S3DIR_XX" in line:
                    line = line.replace("XX_S3DIR_XX", args.s3dir)

                if "XX_BASE_URL_XX" in line:
                    line = line.replace("XX_BASE_URL_XX", args.signpost_base_url)

                if "XX_MEM_XX" in line:
                    line = line.replace("XX_MEM_XX", str(args.mem))

                if "XX_THREAD_COUNT_XX" in line:
                    line = line.replace("XX_THREAD_COUNT_XX", str(args.thread_count))


                slurm.write(line)
            slurm.close()
            temp.close()