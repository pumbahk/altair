import os
import shutil
import functools
from fnmatch import fnmatch
import logging
logger = logging.getLogger(__name__)

from .refine import refine_link_as_string

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
            if f.endswith(".html"):
                output = refine_link_as_string(f, root, event.static_directory)
                path = os.path.join(root, f)
                os.rename(path, path+".original")
                with open(path, "w") as wf:
                    wf.write(output)

def s3upload_directory(after_create):
    event = after_create
    event.static_directory.upload_directory(event.root)
