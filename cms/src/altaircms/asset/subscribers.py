## after file s3 upload, set file_url  attribute of asset model
from collections import defaultdict
import os.path
from functools import wraps
from . import SESSION_NAME
from altaircms.filelib.s3 import Renamer
import logging
logger = logging.getLogger(__name__)

def normalize_url(filename):
    return os.path.splitext(os.path.basename(filename))[0]

def make_s3url(bucket_name, uploaded_name):
    return "s3://{0}/{1}".format(bucket_name.rstrip("/"), uploaded_name.lstrip("/"))

def make_s3_upload_filename(request, filename):
    return "{0}/{1}/{2}".format(SESSION_NAME, request.organization.short_name, filename.lstrip("/"))

def only_asset(fn):
    @wraps(fn)
    def wrapped(event):
        session = event.session
        if session.marker != SESSION_NAME:
            return
        return fn(event)
    return wrapped

@only_asset
def unpublish_files_on_s3(after_s3_delete):
    event = after_s3_delete
    request = event.request
    assets = event.extra_args
    uploader = event.uploader
    logger.warn("*debug unpublish_deleted_files_on_s3 start. assets={0}".format(assets))
    for asset in assets:
        for filename in asset.all_files_candidates():
            filename = make_s3_upload_filename(request, filename)
            logger.warn("*debug unpublish key name={0}".format(filename))
            uploader.unpublish(filename, check=True)
unpublish_deleted_files_on_s3 = unpublish_files_on_s3

@only_asset
def publish_files_on_s3(after_s3_delete):
    event = after_s3_delete
    request = event.request
    assets = event.extra_args
    uploader = event.uploader
    logger.warn("*debug publish_files_on_s3 start. assets={0}".format(assets))
    for asset in assets:
        for filename in asset.all_files_candidates():
            filename = make_s3_upload_filename(request, filename)
            logger.warn("*debug publish key name={0}".format(filename))
            uploader.publish(filename, check=True)

@only_asset
def set_file_url(after_s3_upload):
    event = after_s3_upload
    assets = event.extra_args
    logger.warn("*debug set_file_url start. assets={0}".format(assets))
    asset_dict = {normalize_url(asset.filepath): asset for asset in assets}
    bucket_name = event.uploader.bucket_name
    s3uploaded_dict = defaultdict(dict)

    for f in event.files:
        if "thumb." in f.name:
            s3uploaded_dict[normalize_url(f.name.replace("thumb.", ""))]["thumbnail_url"] = make_s3url(bucket_name, f.name)
        else:
            s3uploaded_dict[normalize_url(f.name)]["file_url"] = make_s3url(bucket_name, f.name)
            
    for k, D in s3uploaded_dict.items():
        asset = asset_dict.get(k)
        if asset:
            asset.file_url = D.get("file_url")
            asset.thumbnail_url = D.get("thumbnail_url")
            logger.warn("*debug file url is set. asset={2} file_url={0} thumbnail_url={1}".format(D.get("file_url"), D.get("thumbnail_url"), asset))

@only_asset
def rename_for_s3_upload(before_s3_upload):
    event = before_s3_upload
    ## foo.jpg -> asset/foo.jpg
    renamer = Renamer(event.request, event)
    renamer.rename(make_s3_upload_filename)
