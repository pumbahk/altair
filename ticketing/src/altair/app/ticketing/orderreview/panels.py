# -*- coding: utf-8 -*-
import logging
import os
import shutil
import uuid

from altair.app.ticketing.cart.rendering import selectable_renderer
from altair.app.ticketing.events.auto_cms.api import s3upload, S3ConnectionFactory
from boto.exception import S3ResponseError
from pyramid_layout.panel import panel_config

from .schemas import PassportUserImageUploadForm
from ..orders.models import Order
from ..passport.api import get_passport_datas
from ..passport.models import PassportUser

S3_DIRECTORY = "passport/static/{}/"
logger = logging.getLogger(__name__)


@panel_config('order_detail.standard', renderer=selectable_renderer('order_review/_order_detail_standard.html'))
@panel_config('order_detail.lot', renderer=selectable_renderer('order_review/_order_detail_lots.html'))
def order_detail_standard(context, request, order, user_point_accounts=None, locale=None):
    return {'order': order, 'user_point_accounts': user_point_accounts, 'locale': locale}


@panel_config('order_detail.booster.89ers', renderer=selectable_renderer('order_review/_order_detail_booster.html'))
@panel_config('order_detail.booster.bambitious',
              renderer=selectable_renderer('order_review/_order_detail_booster.html'))
@panel_config('order_detail.booster.bigbulls', renderer=selectable_renderer('order_review/_order_detail_booster.html'))
def order_detail_booster(context, request, order, user_point_accounts=None, locale=None):
    return {'order': order, 'user_point_accounts': user_point_accounts, 'locale': locale}


@panel_config('order_detail.fc', renderer=selectable_renderer('order_review/_order_detail_fc.html'))
def order_detail_fc(context, request, order, user_point_accounts=None, locale=None):
    return {'order': order, 'user_point_accounts': user_point_accounts, 'locale': locale}


@panel_config('order_detail.goods', renderer=selectable_renderer('order_review/_order_detail_goods.html'))
def order_detail_goods(context, request, order, user_point_accounts=None, locale=None):
    return {'order': order, 'user_point_accounts': user_point_accounts, 'locale': locale}


@panel_config('order_detail.passport', renderer=selectable_renderer('order_review/_order_detail_passport.html'))
def order_detail_passport(context, request, order, user_point_accounts=None, locale=None):
    upload_form = PassportUserImageUploadForm(request.POST)
    if upload_form.passport_user_id.data:
        if not isinstance(upload_form['upload_file'].data, unicode):
            # パスポート画像がPOSTされた
            s3_file_path = save_upload_file(request, upload_form)
            update_passport_user_image(upload_form, s3_file_path)
            order = Order.get(order.id, order.organization_id)
        else:
            request.session.flash(u'ファイルを指定してアップロードしてください')

    passport_infos = []
    if order.performance.passport:
        passport_infos = get_passport_datas(order)

    forms = []
    for info in passport_infos:
        form = PassportUserImageUploadForm(request.POST)
        form.passport_user_id.data = info._passport_user.id
        forms.append(form)

    return {'order': order, 'user_point_accounts': user_point_accounts, 'locale': locale,
            'passport_infos': passport_infos, 'forms': forms}


def update_passport_user_image(upload_form, s3_file_path):
    user = PassportUser.get(upload_form.passport_user_id.data)
    user.image_path = s3_file_path
    user.save()


def save_upload_file(request, form):
    # ファイルをサーバに作成、S3にアップロード後、サーバのファイルを削除
    filename = form['upload_file'].data.filename
    input_file = form['upload_file'].data.file
    temp_file_path = os.path.join('/tmp', '{}.upload_file'.format(uuid.uuid4())) + '~'
    input_file.seek(0)
    with open(temp_file_path, 'wb') as output_file:
        shutil.copyfileobj(input_file, output_file)
    file_path = "/tmp/{}".format(filename.encode('utf_8'))
    os.rename(temp_file_path, file_path)
    connection = S3ConnectionFactory(request)()
    bucket_name = request.registry.settings["s3.bucket_name"]

    s3_file_path = ""
    try:
        s3_file_path = s3upload(connection, bucket_name, file_path, S3_DIRECTORY.format(form.passport_user_id.data),
                                "{0}.jpg".format(uuid.uuid4()))

    except S3ResponseError as e:
        logger.error("Image did not save. PerformanceID={}".format(form.passport_user_id.data))
        request.session.flash(u"{}の画像が保存できませんでした。PassportUserID:{}".format(form.passport_user_id.data))
    os.remove(file_path)
    return s3_file_path
