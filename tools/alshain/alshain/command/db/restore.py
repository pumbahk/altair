# -*- coding: utf-8 -*-
import os
import tempfile
import urlparse
from ... import utils


class StatusError(Exception):
    pass


def generate_snapshot_url():
    cmd = "s3cmd ls `s3cmd ls s3://ticketstar-db-dev-snapshots | grep -v 'tainted' | tail -n 1 | awk '{print $2}'` | awk '{print $4}'"
    out = tempfile.TemporaryFile()
    child = utils.call(cmd, shell=True, stdout=out)
    if 0 == child.wait():
        out.seek(0)
        for line in out:
            line = line.strip()
            if line:
                yield line
    else:
        raise StatusError('illigal status: {0}'.format(child.return_code))


def download_snapshot(url):
    cmd = 's3cmd get -f "{0}"'.format(url)
    print cmd
    utils.call(cmd).wait()
    res = urlparse.urlparse(url)
    return os.path.basename(res.path)


def restore_sql(path):
    xz = path
    db = 'ticketing' if 'ticketing' in xz else 'altaircms'
    cmd = 'xz -cd {xz} | mysql -u root {db}'.format(xz=xz, db=db)
    print cmd
    utils.Shell.system(cmd)


def main(argv):
    for url in generate_snapshot_url():
        print 'download {0}'.format(url)
        path = download_snapshot(url)

        print 'resotre {0}'.format(path)
        restore_sql(path)

if __name__ == '__main__':
    main()
