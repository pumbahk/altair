from datetime import datetime


def calc_version(dist, attr, value):
    if not value or not attr == 'use_date_versioning':
        return

    print "use_date_versioning"
    dist.metadata.version = date_version()
    print "version = %s" % dist.metadata.version


def date_version():
    now = datetime.now()
    return now.strftime("%Y%m%d%H%M")
