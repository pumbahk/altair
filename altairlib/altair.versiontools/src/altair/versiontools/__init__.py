from datetime import datetime
import subprocess

def calc_version(dist, attr, value):
    if not value or not attr == 'use_date_versioning':
        return

    print "use_date_versioning"
    dist.metadata.version = "%s.%s" % (date_version(), git_rev())
    print "version = %s" % dist.metadata.version


def date_version():
    now = datetime.now()
    return now.strftime("%Y%m%d%H%M")

def git_rev():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'])[:7]
