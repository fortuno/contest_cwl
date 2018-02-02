'''
Postgres mixins
'''
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.dialects.postgresql import ARRAY
from contextlib import contextmanager

class StatusTypeMixin(object):
    """ Gather information about processing status """
    id               = Column(Integer, primary_key=True)
    uuid             = Column(String)
    tumor_bam_uuid   = Column(String)    
    project          = Column(String)    
    case_id          = Column(String) 
    status           = Column(String)
    s3_url           = Column(String)
    datetime_start   = Column(String)
    datetime_end     = Column(String)
    md5              = Column(String)
    file_size        = Column(String)
    hostname         = Column(String)
    cwl_version      = Column(String)
    docker_version   = Column(ARRAY(String))

    def __repr__(self):
        return "<StatusTypeMixin(uuid='%s', status='%s' , s3_url='%s')>" %(self.uuid, self.status, self.s3_url)

class MetricsTypeMixin(object):
    ''' Gather timing metrics with input uuids '''
    id                        = Column(Integer, primary_key=True)
    uuid                      = Column(String)
    case_id                   = Column(String)     
    download_time             = Column(String)
    upload_time               = Column(String)
    thread_count              = Column(String)
    elapsed                   = Column(String)
    systime                   = Column(Float)
    usertime                  = Column(Float)
    walltime                  = Column(String)
    percent_of_cpu            = Column(Float)
    maximum_resident_set_size = Column(Float)
    status                    = Column(String)

    def __repr__(self):
        return "<TimeToolTypeMixin(uuid='%s', whole_workflow_elapsed='%s', status='%s')>" %(self.uuid, self.whole_workflow_elapsed, self.status)