## after file s3 upload, set file_url  attribute of asset model
from collections import defaultdict
import os.path
from . import SESSION_NAME

def normalize(f):
    return os.path.splitext(os.path.basename(f.name))[0]

def make_s3url(bucket_name, filename):
    return "s3://{0}/{1}".format(bucket_name.rstrip("/"), filename.lstrip("/"))

def set_file_url(after_s3_upload):
    session = after_s3_upload.session
    if session.marker != SESSION_NAME:
        return

    bucket_name = after_s3_upload.uploader.bucket_name
    D = defaultdict(dict)
    for f in after_s3_upload.files:
        if "thumb." in f.name:
            D[normalize(f.name.replace("thumb."))]["thumbnail_url"] = make_s3url(bucket_name, f.name)
        else:
            D[normalize(f.name)]["file_url"] = make_s3url(bucket_name, f.name)
    request = after_s3_upload.request


