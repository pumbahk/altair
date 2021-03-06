# -*- coding:utf-8 -*-
import os
import sys
from lxml import html
import uuid
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARN)
import argparse

from boto.s3.connection import S3Connection
from pyramid.paster import bootstrap
from pyramid.path import AssetResolver

from altaircms.page.staticupload.refine import (
    get_html_parser,
    DEFAULT_ENCODING,
    is_html_filename
    )
from altair.pyramid_boto.s3.connection import DefaultS3Uploader


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

def fix_url_recursive(path, static_pageset, bucket_name):
    for root, ds, fs in os.walk(path):
        for f in fs:
            if not f.startswith(".") and is_html_filename(f):
                fix_url(os.path.join(root, f), static_pageset, bucket_name)

def fix_url(fname, static_pageset, bucket_name):
    doc = html.parse(fname, parser=get_html_parser(DEFAULT_ENCODING)).getroot()
    if doc is None:
        logger.warn("replace: {fname} is none".format(fname=fname))
        return 
    prefix = "/{}/{}/".format(static_pageset.organization.short_name, static_pageset.url)
    replaced = "/{}/{}/".format(static_pageset.organization.short_name, static_pageset.hash)
    target_s3 = "{bucket}.s3.amazonaws.com".format(bucket=bucket_name)
    def link_repl(href):
        if target_s3 in href:
            if prefix in href:
                href = href.replace(prefix, replaced)
            if href.startswith("http:"):
                href = href.replace("http:", "", 1)
        return href
    doc.rewrite_links(link_repl)
    with open(fname, "w") as wf:
        wf.write(html.tostring(doc, pretty_print=True, encoding=DEFAULT_ENCODING))

def move_s3(request, root):
    from altaircms.page.staticupload.api import get_static_page_utility
    utility=get_static_page_utility(request)
    utility.upload_directory(root)
    # uploader.copy_items(src, dst, recursive=True)

def _main(args):
    from altaircms.page.models import StaticPageSet
    from altaircms.auth.models import Organization
    from altaircms.models import DBSession
    env = bootstrap(args.config)
    request = env["request"]
    base = AssetResolver().resolve(request.registry.settings["altaircms.page.static.directory"]).abspath()

    bucket_name = request.registry.settings["s3.bucket_name"]
    for sp in StaticPageSet.query.filter(StaticPageSet.hash=="").all():
        try:
            ##slackoff
            sp.organization = Organization.query.filter_by(id=sp.organization_id).one()

            basedir = get_basepath(base, sp)
            sp.hash = uuid.uuid4().hex
            DBSession.add(sp)
            fix_url_recursive(os.path.join(basedir, sp.url), sp, bucket_name)
            move_fs(basedir, sp.url, sp.hash)
            move_s3(request, os.path.join(basedir, sp.hash))
            sys.stderr.write(".")
        except Exception as e:
            logger.error(str(e))
    import transaction
    transaction.commit()
        
if __name__ == "__main__":
    main()
