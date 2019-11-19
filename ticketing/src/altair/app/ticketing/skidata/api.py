# -*- coding: utf-8 -*-

from altair.app.ticketing.skidata.models import SkidataBarcode
from altair.app.ticketing.orders.models import OrderedProductItemToken


def create_new_barcode(order_no):
    # TODO 試合当日はSKIDATAと連携
    opi_tokens = OrderedProductItemToken.find_all_by_order_no(order_no)
    for token in opi_tokens:
        SkidataBarcode.insert_new_barcode(token.id)
