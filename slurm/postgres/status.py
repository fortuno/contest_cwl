'''
Postgres tables for the PDC CWL Workflow
'''
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, mapper
from sqlalchemy import MetaData, Table
from sqlalchemy import Column, String

def get_status(upload_exit, cwl_exit, upload_file_location, upload_dir_location, logger):
    """ update the status of job on postgres """
    loc = 'UNKNOWN'
    status = 'UNKNOWN'
    if upload_exit == 0:
        loc = upload_file_location
        if cwl_exit == 0:
            status = 'COMPLETED'
            logger.info("uploaded all files to object store. The path is: %s" % upload_dir_location)
        else:
            status = 'CWL_FAILED'
            logger.info("CWL failed. The log path is: %s" % upload_dir_location)
    else:
        loc = 'Not Applicable'
        if cwl_exit == 0:
            status = 'UPLOAD_FAILURE'
            logger.info("Upload of files failed")
        else:
            status = 'FAILED'
            logger.info("CWL and upload both failed")
    return(status, loc)

class State(object):
    pass

class Files(object):
    pass

def get_tn_cases(engine, input_table):
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    meta = MetaData(engine)

    #read the status table
    files = Table(input_table, meta,
                  Column("raw_snp_vcf_id", String, primary_key=True),
                  autoload=True)

    mapper(Files, files)

    s = [i for i in session.query(Files).all()]

    return s