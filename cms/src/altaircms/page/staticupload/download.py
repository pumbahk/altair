# -*- coding: utf-8 -*-
## download manager
import logging
logger = logging.getLogger(__name__)

import os.path
import shutil
import isodate
from pyramid.decorator import reify
from datetime import datetime
from pyramid.httpexceptions import HTTPNotFound

from altaircms.viewlib import download_response
from altaircms.filelib import zipupload
from altaircms.filelib.s3 import get_s3_utility_factory


class ZippedStaticFileManager(object):
    def __init__(self, request, static_page, tmpdir, downloader=None):
        self.request = request
        self.static_page = static_page
        self.tmpdir = tmpdir
        self.downloader = downloader

    @property
    def normalname(self):
        static_page = self.static_page
        return u"{prefix}.{id}.{suffix}.zip".format(prefix=static_page.pageset.url, id=static_page.id, suffix=static_page.updated_at.strftime("%Y%m%d%H%M"))

    @property
    def filename(self):
        return self.normalname.replace("/", "-")

    @property
    def zippath(self):
        return os.path.join(self.tmpdir, self.normalname)

    def exists(self, path):
        return os.path.exists(path)

    def get_fetchtime(self, absroot):
        memopath = os.path.join(absroot, ".fetchtime")
        if self.exists(memopath):
            return isodate.parse_datetime(open(memopath).read())
        else:
            return datetime(1900, 1, 1)

    def need_download(self, absroot):
        return not self.exists(absroot) or self.get_fetchtime(absroot) < self.static_page.uploaded_at

    def create_zip(self, absroot, writepath):
        if self.downloader is None:
            logger.warn("static page(id={id}) is not uploaded. and absroot(={absroot}) is not found".format(id=self.static_page.id, absroot=absroot))
        elif self.need_download(absroot):
            self.downloader.download_recursively(absroot)
        with zipupload.current_directory(absroot):
            zipupload.create_zipfile_from_directory(".", writepath, self.downloader.file_list)

    def download_response(self, absroot, path=None, filename=None):
        path = path or self.zippath
        filename = filename or self.filename
        logger.info("zippath: {path}".format(path=path))
        if not self.exists(path):
            self.create_zip(absroot, path)
        return download_response(path=path,request=self.request, filename=filename) 

class S3Downloader(object):
    @reify
    def bucket(self):
        return get_s3_utility_factory(self.request).bucket

    def __init__(self, request, static_page, prefix=""): ## slackoff
        self.request = request
        self.static_page = static_page
        # データベースの記録にあるファイルをリストに入れる。
        # $がついてるやつはフォルダのため入れない。
        # .originalがついてるやつはバックアップのため入れない。
        self.file_list = [f for f in self.static_page.file_structure.keys()
                          if not f.endswith('$') and not f.endswith('.original')]
        self.prefix = prefix
        self.filters = []

    def add_filter(self, fn):
        self.filters.append(fn)

    def download_recursively(self, absroot):
        if self.static_page.uploaded_at is None:
            logger.error("static page(id={id}) is not uploaded.".format(id=self.static_page.id))
            raise HTTPNotFound("")

        now = datetime.now()
        memopath = os.path.join(absroot, ".downloadtime")
        if not os.path.exists(absroot):
            os.makedirs(absroot)
        with open(memopath, "w") as wf:
            wf.write(now.isoformat())
        return self._download_recursively(absroot)

    def _download_recursively(self, absroot):
        bucket = self.bucket
        logger.info("download: bucket={bucket} prefix={prefix}".format(bucket=bucket.name, prefix=self.prefix))
        for io in bucket.list(prefix=self.prefix):
            subname = io.name.replace(self.prefix, "").lstrip("/")
            # データベースの記録にないファイルを処理しない。
            if not self._check_file_in_db_record(subname):
                continue
            writepath = os.path.join(absroot, subname)
            dirname = os.path.dirname(writepath)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            with open(writepath, "w") as wf:
                for f in self.filters:
                    io = f(io, subname)
                shutil.copyfileobj(io, wf)

    # 対象ファイルはデータベースの記録にあるかどうかをチェックする。
    def _check_file_in_db_record(self, subname):
        return subname in self.file_list
