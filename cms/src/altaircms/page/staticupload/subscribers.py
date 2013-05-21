import os
import shutil
import json
import functools
from datetime import datetime
from fnmatch import fnmatch
import logging
logger = logging.getLogger(__name__)

from .refine import refine_link_as_string, is_html_filename

def _delete_ignorefile_after_staticupload(ignore_directories, ignore_files, after_create):
    event = after_create
    for root, dirs, files in os.walk(event.root):
        for d in dirs:
            if d in ignore_directories:
                logger.warn("*debug staticupload delete ignore directories: {0}".format(d))
                shutil.rmtree(os.path.join(root, d))
        for f in files:
            if any(fnmatch(f, case) for case in ignore_files):
                logger.warn("*debug staticupload delete ignore files: {0}".format(f))
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

## after create -> (s3upload) -> after zipupload
def s3upload_directory(after_zipupload):
    event = after_zipupload
    static_directory = event.static_directory
    static_page = event.static_page
    absroot = event.root
    static_directory.upload_directory(absroot)
    static_page.uploaded_at = datetime.now()

