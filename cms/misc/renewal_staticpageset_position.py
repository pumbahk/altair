# -*- coding:utf-8 -*-
import os
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARN)
import argparse
from pyramid.paster import bootstrap
from pyramid.path import DottedNameResolver
from altaircms.page.static_upload.refine import get_html_parser, DEFAULT_ENCODING
from boto import connect_s3
from boto.s3.key import Key
from lxml import html
import uuid

def main():
    parser = argparse.ArgumentParser(description="renweal a position of data about static pageset. using hash(uuid4)")
    parser.add_argument("config", help=u"development.ini'")
    args = parser.parse_args()
    _main(args)

def get_basepath(basedir, static_pageset):
    return os.path.join(basedir, static_pageset.organization.short_name)

def move_fs(basepath, src, dst):
    if not os.path.exists(os.path.join(basepath, src)):
        logger.warn("fs: {path} is not found".format(path=basepath))
        return 
    os.rename(os.path.join(basepath, src), os.path.join(basepath, dst))

def fix_url(fname, static_pageset, bucket_name):
    doc = html.parse(fname, parser=get_html_parser(DEFAULT_ENCODING)).getroot()
    if doc is None:
        logger.warn("replace: {fname} is none".format(fname=fname))
        return 
    prefix = "/{}/{}/".format(static_pageset.organization.short_name, static_pageset.url)
    replaced = "/{}/{}/".format(static_pageset.organization.short_name, static_pageset.hash)
    target_s3 = "{bucket}.s3.amazonaws.com".format(bucket=bucket_name)
    def link_repl(href):
        if all(x in href for x in [target_s3, prefix]):
            href = href.replace(prefix, replaced)
        return href
    doc.rewrite_links(link_repl)
    with open(fname, "w") as wf:
        wf.write(html.tostring(doc, pretty_print=True, encoding=DEFAULT_ENCODING))

def move_s3(bucket, src, dst):
    k=Key(bucket)
    k.key=src
    k.copy(bucket, dst)
    k.delete()

def normalize_s3(sp, path):
    return "usersite/uploaded/{organization}/{path}".format(organization=sp.organization.short_name, path=path)

def _main(args):
    from altaircms.page.models import StaticPageSet
    from altaircms.models import DBSession
    env = bootstrap(args.config)
    request = env["request"]
    base = DottedNameResolver().resolve(request.registry.settings["altaircms.page.static.directory"])

    bucket_name = request.registry.settings["s3.bucket_name"]
    c = connect_s3()
    bucket = c.get_bucket(bucket_name)
    for sp in StaticPageSet.query.filter(hash=="").all():
        try:
            basedir = get_basepath(base, sp)
            sp.hash = uuid.uuid4().hex
            DBSession.add(sp)
            fix_url(os.path.join(basedir, sp.url), sp, bucket_name)
            move_fs(basedir, sp.url, sp.hash)
            move_s3(bucket, normalize_s3(sp, sp.url), normalize_s3(sp, sp.hash))
        except Exception as e:
            logger.error(str(e))
    import transaction
    transaction.commit()
        
if __name__ == "__main__":
    main()
