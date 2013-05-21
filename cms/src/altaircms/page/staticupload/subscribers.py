import os
import shutil
import functools
from fnmatch import fnmatch
import logging
logger = logging.getLogger(__name__)

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
