# -*- coding: utf-8 -*-
from altair.formhelpers.fields import OurFormField

from . import api
from . import schemas


def create_form(request, context, *args, **kwds):
    """希望入力と配送先情報と追加情報入力用のフォームを返す
    """

    def _form_factory(formdata, name_builder, **kwargs):
        form = schemas.DynamicExtraForm(
            formdata=formdata, name_builder=name_builder,
            context=context, **kwargs)
        return form

    fields = [
        ('extra', OurFormField(
            form_factory=_form_factory, name_handler=u'.',
            field_error_formatter=None)),
        ]
    flavors = context.cart_setting.flavors or {}
    form = api.create_client_form(
        context, request, flavors=flavors,
        _fields=fields, **kwds)
    return form
