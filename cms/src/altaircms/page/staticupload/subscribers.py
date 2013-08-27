import os
import shutil
import json
import functools
from datetime import datetime
from fnmatch import fnmatch
from altaircms.models import DBSession
import logging
logger = logging.getLogger(__name__)

from .refine import refine_link_as_string, is_html_filename

def _delete_ignorefile_after_staticupload(ignore_directories, ignore_files, after_create):
    event = after_create
    for root, dirs, files in os.walk(event.root):
        for d in dirs:
            if d in ignore_directories:
                logger.info("*debug staticupload delete ignore directories: {0}".format(d))
                shutil.rmtree(os.path.join(root, d))
        for f in files:
            if any(fnmatch(f, case) for case in ignore_files):
                logger.info("*debug staticupload delete ignore files: {0}".format(f))
                os.remove(os.path.join(root, f))

IGNORE_DIRECTORIES = ["__MACOSX", ".AppleDouble", ".LSOverride", ".svn", ".git", ".hg"]
IGNORE_FILES = [".DS_Store","*.swp", "*.out", "*.bak", "*.lock", "[tT]humbs.db", "ehthumbs.db", "[dD]esktop.ini"]
delete_ignorefile_after_staticupload = functools.partial(_delete_ignorefile_after_staticupload, IGNORE_DIRECTORIES, IGNORE_FILES)


def refine_html_files_after_staticupload(after_create):
    event = after_create
    for root, dirs, files in os.walk(event.root):
        for f in files:
            if is_html_filename(f):
                output = refine_link_as_string(f, root, event.static_directory)
                path = os.path.join(root, f)
                os.rename(path, path+".original")
                with open(path, "w") as wf:
                    wf.write(output)

def refine_html_file_after_staticupload(partial_create):
    event = partial_create
    path = event.root
    dirname, f = os.path.split(path)
    output = refine_link_as_string(f, dirname, event.static_directory)
    os.rename(path, path+".original")
    with open(path, "w") as wf:
        wf.write(output)

## after create -> (s3upload) -> after zipupload
def s3upload_directory(after_zipupload):
    event = after_zipupload
    static_directory = event.static_directory
    static_page = event.static_page
    absroot = event.root
    try:
        static_directory.upload_directory(absroot)
    except Exception as e:
        logger.exception(str(e))
        logger.error("static page: s3upload failure. absroot={0}".format(absroot))
    ## update uploaded_at
    static_page.uploaded_at = datetime.now()
    DBSession.add(static_page)

def s3clean_directory(after_model_delete):
    event = after_model_delete
    static_directory = event.static_directory
    absroot = event.root
    try:
        static_directory.clean_directory(absroot)
    except Exception as e:
        logger.exception(str(e))
        logger.error("static page: s3clean directory failure. absroot={0}".format(absroot))


from functools import wraps
def for_event(fn):
    @wraps(fn)
    def wrapped(event):
        return fn(event.request, event.root, event.static_page, event.static_directory)
    return wrapped

@for_event
def s3delete_file(request, root, static_page, static_directory):
    static_directory.delete_file(os.path.dirname(root), os.path.basename(root))
    ## update uploaded_at
    static_page.uploaded_at = datetime.now()
    DBSession.add(static_page)

@for_event
def s3update_file(request, root, static_page, static_directory):
    static_directory.upload_file(os.path.dirname(root), os.path.basename(root))
    ## update uploaded_at
    static_page.uploaded_at = datetime.now()
    DBSession.add(static_page)

def s3delete_files_completely(after_delete_completely):
    event = after_delete_completely
    static_directory = event.static_directory
    static_pageset = event.static_pageset
    uploader = static_directory.s3utility.uploader
    name = "{0}/{1}/{2}".format(static_directory.prefix, event.request.organization.short_name, static_pageset.hash)
    try:
        logger.warn("delete all completely!! danger danger,  src=%s" % name)
        delete_candidates = list(uploader.bucket.list(name))
        uploader.unpublish_items(delete_candidates)
    except Exception as e:
        logger.exception(str(e))
        logger.error("static page: s3delete files completely. name={0}".format(name))

def s3rename_uploaded_files(after_change_directory):
    event = after_change_directory
    static_directory = event.static_directory
    static_directory.s3utility.uploader.copy_items(
        static_directory.get_name(*os.path.split(event.src)), 
        static_directory.get_name(*os.path.split(event.dst)), 
        recursive=True)
   
def update_model_file_structure(after_zipupload):
    event = after_zipupload
    static_page = event.static_page
    static_directory = event.static_directory
    return _update_model_file_structure(static_page, static_directory.get_rootname(static_page))

def _update_model_file_structure(static_page, absroot):
    ## model update
    inspection_targets = {}
    for root, dirs, files in os.walk(absroot):
        for d in dirs:
            inspection_targets[os.path.join(root.replace(absroot, ""), d).lstrip("/")+"$"] = 1            
        for f in files:
            inspection_targets[os.path.join(root.replace(absroot, ""), f).lstrip("/")] = 1
    static_page.file_structure_text = json.dumps(inspection_targets)

def delete_completely_filesystem(after_delete_completely):
    event = after_delete_completely
    static_directory = event.static_directory
    root = static_directory.get_toplevelname(event.static_pageset)
    shutil.rmtree(root)
