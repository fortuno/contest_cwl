"""Module for running commands, getting file stats, and
setting up logging.
"""
import logging
import hashlib
import subprocess
import os
import json
import shutil
from functools import partial
from multiprocessing.dummy import Pool, Lock
from itertools import islice

def fai_chunk(fai_path, blocksize):
    #function for getting genome chunk from reference fai file
  seq_map = {}
  with open(fai_path) as handle:
    head = list(islice(handle, 25))
    for line in head:
      tmp = line.split("\t")
      seq_map[tmp[0]] = int(tmp[1])
    for seq in seq_map:
        l = seq_map[seq]
        for i in range(1, l, blocksize):
            yield (seq, i, min(i+blocksize-1, l))

def fai_chunk_chr(fai_path):
    #function for getting genome chunk from reference fai file
  chromosomes = []
  with open(fai_path) as handle:
    head = list(islice(handle, 25))
    for line in head:
      tmp = line.split("\t")
      chromosomes.append(tmp[0])

  return chromosomes


def do_pool_commands(cmd, logger, lock = Lock()):

    output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = output.communicate()
    with lock:
        logger.info('running chunk call: %s' % cmd)        
        logger.info('output communicate: %s' % stdout)
        logger.info('error communicate: %s' % stderr)
    return output.wait()

def multi_commands(cmds, thread_count, logger):
    pool = Pool(int(thread_count))
    output = pool.map(partial(do_pool_commands, logger=logger), cmds)
    return output

def setup_logging(log_name, log_filename=None):
    """ 
    Sets up a logger
    """
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO)

    if log_filename is None:
        ch = logging.StreamHandler()
    else:
        ch = logging.FileHandler(log_filename, mode='w')

    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(levelname)s] [%(asctime)s] [%(name)s] - %(message)s',
                                  datefmt='%H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

def get_md5(input_file):
    '''Estimates md5 of file '''
    BLOCKSIZE = 65536
    hasher = hashlib.md5()
    with open(input_file, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()

def get_time_metrics(time_file):
    ''' Extract time file outputs '''
    time_metrics = {
      "system_time": [],
      "user_time": [],
      "wall_clock": [],
      "percent_of_cpu": [],
      "maximum_resident_set_size": []
    }
    try:
        with open(time_file, "rt") as fh:
            for line in fh:
                line = line.strip()
                if 'User time (seconds):' in line:
                    time_metrics['user_time'].append(float(line.split(':')[-1].strip()))
                if 'System time (seconds):' in line:
                    time_metrics['system_time'].append(float(line.split(':')[-1].strip()))
                if 'Percent of CPU this job got:' in line:
                    time_metrics['percent_of_cpu'].append(float(line.split(':')[-1].strip().rstrip('%')))
                if 'Elapsed (wall clock) time (h:mm:ss or m:ss):' in line:
                    value = ":".join(line.split(":")[4:])
                    #hour case
                    if value.count(':') == 2:
                        hours = int(value.split(':')[0])
                        minutes = int(value.split(':')[1])
                        seconds = float(value.split(':')[2])
                        total_seconds = (hours * 60 * 60) + (minutes * 60) + seconds
                        time_metrics['wall_clock'].append(float(total_seconds))
                    if value.count(':') == 1:
                        minutes = int(value.split(':')[0])
                        seconds = float(value.split(':')[1])
                        total_seconds = (minutes * 60) + seconds
                        time_metrics['wall_clock'].append(float(total_seconds))
                if ('Maximum resident set size (kbytes):') in line:
                    time_metrics['maximum_resident_set_size'].append(float(line.split(':')[-1].strip()))
    except: pass

    return time_metrics

def get_file_size(filename):
    ''' Gets file size '''
    fstats = os.stat(filename)
    return fstats.st_size

def run_command(cmd, logger=None, shell_var=False):
    '''
    Runs a subprocess
    '''
    child = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell_var)
    stdoutdata, stderrdata = child.communicate()
    exit_code = child.returncode

    if logger is not None:
        logger.info(cmd)
        stdoutdata = stdoutdata.split("\n")
        for line in stdoutdata:
            logger.info(line)

        stderrdata = stderrdata.split("\n") 
        for line in stderrdata:
            logger.info(line)
            if 'getMeanInsertSize' in line:
                exit_code = 99

    return exit_code

def remove_dir(dirname):
    """ Remove a directory and all it's contents """

    if os.path.isdir(dirname):
        shutil.rmtree(dirname)
    else:
        raise Exception("Invalid directory: %s" % dirname)


def load_json(filename):
    """ Load json file into dictionary """

    with open(filename, 'r') as fh:
        data = json.load(fh)

    return data

def get_index(logger, inputdir, input_bam):
    """ Build input bam file index """ 
    base, ext = os.path.splitext(os.path.basename(input_bam))
    bai_file = os.path.join(inputdir, base) + ".bai"
    index_cmd = ['samtools', 'index', input_bam]
    index_exit = run_command(index_cmd, logger)
    if index_exit == 0:
        logger.info("Build %s index successfully" % os.path.basename(input_bam))
        os.rename(input_bam+".bai", bai_file)
    else:
        logger.info("Failed to build %s index" % os.path.basename(input_bam))
        sys.exit(index_exit)
    return bai_file
