## after file s3 upload, set file_url  attribute of asset model
from collections import defaultdict
import os.path
from . import SESSION_NAME

import logging
logger = logging.getLogger(__name__)

def normalize(filename):
    return os.path.splitext(os.path.basename(filename))[0]

def make_s3url(bucket_name, filename):
    return "http://s3.amazonaws.com/{0}/{1}".format(bucket_name.rstrip("/"), filename.lstrip("/"))

def set_file_url(after_s3_upload):
    session = after_s3_upload.session
    if session.marker != SESSION_NAME:
        return

    assets = after_s3_upload.extra_args
    logger.warn("*debug set_file_url start. assets={0}".format(assets))
    asset_dict = {normalize(asset.filepath): asset for asset in assets}
    bucket_name = after_s3_upload.uploader.bucket_name
    s3uploaded_dict = defaultdict(dict)

    for f in after_s3_upload.files:
        if "thumb." in f.name:
            s3uploaded_dict[normalize(f.name.replace("thumb.", ""))]["thumbnail_url"] = make_s3url(bucket_name, f.name)
        else:
            s3uploaded_dict[normalize(f.name)]["file_url"] = make_s3url(bucket_name, f.name)
            
    for k, D in s3uploaded_dict.items():
        asset = asset_dict.get(k)
        if asset:
            asset.file_url = D.get("file_url")
            asset.thumbnail_url = D.get("thumbnail_url")
            logger.warn("*debug file url is set. asset={2} file_url={0} thumbnail_url={1}".format(D.get("file_url"), D.get("thumbnail_url"), asset))
