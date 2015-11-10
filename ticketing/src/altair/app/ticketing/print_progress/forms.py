# -*- coding: utf-8 -*-
from altair.formhelpers.form import OurForm
from altair.formhelpers.fields import OurSelectField
from altair.app.ticketing.core.models import (
    ProductItem
    )


class PrintProgressForm(OurForm):
    def __init__(self, formdata=None, obj=None, prefix='', performance_ids=None, **kwargs):
        self.product_items = dict()
        self.product_items[None] = u"すべて"
        for item in ProductItem.query.filter(ProductItem.performance_id.in_(performance_ids)):
            self.product_items[str(item.id)] = item.name
        super(PrintProgressForm, self).__init__(formdata, obj, prefix, **kwargs)

    product_item_id = OurSelectField(
        label=u'商品明細',
        choices=lambda field: [(key, value) for key, value in sorted(field._form.product_items.items())],
        coerce=str
    )
