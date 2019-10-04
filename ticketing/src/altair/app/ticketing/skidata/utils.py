# -*- coding: utf-8 -*-

from altair.app.ticketing.skidata import (
    QR_STR_PREFIX,
    QR_CHARACTERS,
    QR_STR_LENGTH,
)
from altair.app.ticketing.utils import rand_string
import qrcode


def issue_new_qr_str():
    """
    QR文字列を新規に払い出す。
    SkidataBarcodeテーブルを参照し、一意となる文字列を発行する
    :return: 払い出されたQR文字列
    """
    from altair.app.ticketing.skidata.models import SkidataBarcode
    qr_str = QR_STR_PREFIX + rand_string(QR_CHARACTERS, QR_STR_LENGTH - len(QR_STR_PREFIX))
    if SkidataBarcode.is_barcode_exist(qr_str):
        return issue_new_qr_str()
    else:
        return qr_str


def write_qr_image_to_stream(qr_content, stream, img_format):
    """
    引き渡されたQR内容を元にQR画像を生成し、streamに書き込む
    :param qr_content: QR内容
    :param stream: 書き込みストリーム
    :param img_format: 画像フォーマット　拡張子を大文字で指定
    """
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
    )
    qr.add_data(qr_content)
    qr.make(fit=True)
    qr_image = qr.make_image()
    qr_image.save(stream, img_format)
