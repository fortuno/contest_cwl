import os
import sys
import subprocess
import logging
import time
import shutil

def run_command(cmd, logger=None, shell_var=False):
    """ Run a subprocess command """
    timecmd = cmd
    timecmd.insert(0, '/usr/bin/time')
    timecmd.insert(1, '-v')

    child = subprocess.Popen(timecmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell_var)
    stdoutdata, stderrdata = child.communicate()
    exit_code = child.returncode

    if logger != None:
        logger.info(cmd)
        stdoutdata = stdoutdata.split("\n")
        for line in stdoutdata:
            logger.info(line)

        stderrdata = stderrdata.split("\n")
        for line in stderrdata:
            logger.info(line)
        logger.info('completed cmd: %s' % str(timecmd))

    return exit_code
    
def upload_to_cleversafe(logger, basedir, cwltool_path, remote_output, local_input, config, credentials, endpoint_json, s3cfg_section):
    """ Upload a file to cleversafe to a folder """

    if (remote_output != "" and (os.path.isfile(local_input) or os.path.isdir(local_input))):
        s3_cwl = basedir + '/contest_cwl/tools/aws_s3_put.cwl'
        cmd = [cwltool_path, s3_cwl, '--aws_config', config, '--aws_shared_credentials', credentials, '--endpoint_json', endpoint_json, '--s3cfg_section', s3cfg_section, '--s3uri', remote_output, '--input', local_input]
        exit_code = run_command(cmd, logger)
    else:
        raise Exception("invalid input %s or output %s" %(local_input, remote_output))
    return exit_code

def remove_dir(dirname):
    """ Remove a directory and all it's contents """

    if os.path.isdir(dirname):
        shutil.rmtree(dirname)
    else:
        raise Exception("Invalid directory: %s" % dirname)