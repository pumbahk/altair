# -*- coding: utf-8 -*-
import logging
import os
import uuid
import shutil
from .api import s3upload, S3ConnectionFactory

from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound
from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.core.models import Event, Performance
from boto.exception import S3ResponseError

S3_DIRECTORY = "auto_cms/static/{}/"
logger = logging.getLogger(__name__)


class AutoCmsImageResource(TicketingAdminResource):
    def __init__(self, request):
        super(AutoCmsImageResource, self).__init__(request)
        if not self.user:
            raise HTTPNotFound()

        try:
            event_id = self.request.matchdict.get('event_id')
            performance_id = self.request.matchdict.get('performance_id')
            self.event = None
            self.performance = None
            if event_id:
                self.event = Event.query.filter(Event.id == long(event_id)).first()
            if performance_id:
                self.performance = Performance.query.filter(Performance.id == long(performance_id)).first()
        except (TypeError, ValueError, NoResultFound):
            raise HTTPNotFound()

    def save_upload_file(self, performances):
        # ファイルをサーバに作成、S3にアップロード後、サーバのファイルを削除
        filename = self.request.POST['upload_file'].filename
        input_file = self.request.POST['upload_file'].file
        temp_file_path = os.path.join('/tmp', '{}.upload_file'.format(uuid.uuid4())) + '~'
        input_file.seek(0)
        with open(temp_file_path, 'wb') as output_file:
            shutil.copyfileobj(input_file, output_file)
        file_path = "/tmp/{}".format(filename.encode('utf_8'))
        os.rename(temp_file_path, file_path)
        connection = S3ConnectionFactory(self.request)()
        bucket_name = self.request.registry.settings["s3.bucket_name"]
        for performance in performances:
            try:
                s3upload(connection, bucket_name, file_path, S3_DIRECTORY.format(performance.id), "main.png")
            except S3ResponseError as e:
                logger.info("Image did not save. PerformanceID = {}".format(performance.id))
                self.request.session.flash(u"{}の画像が保存できませんでした。ID:{}".format(performance.name, performance.id))

        os.remove(file_path)
