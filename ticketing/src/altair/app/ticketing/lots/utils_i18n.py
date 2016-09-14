# -*- coding: utf-8 -*-
from datetime import date
from altair.formhelpers.fields import OurFormField

from . import api
from . import schemas
from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.users.models import SexEnum
from .forms_i18n import ClientFormFactory
from altair.app.ticketing.cart.forms_i18n import ClientFormFactory as Cart_ClientFormFactory
def create_form(request, context, formdata=None, **kwds):
    """希望入力と配送先情報と追加情報入力用のフォームを返す(English)
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
    data = None

    if formdata is None:
        # デフォルト値で populate
        user = cart_api.get_or_create_user(context.authenticated_user())
        if context.membershipinfo is not None and \
           context.membershipinfo.enable_auto_input_form and \
           user is not None and user.user_profile is not None:
            user_profile = user.user_profile
            data = dict(
                last_name=user_profile.last_name,
                last_name_kana=user_profile.last_name_kana,
                first_name=user_profile.first_name,
                first_name_kana=user_profile.first_name_kana,
                tel_1=user_profile.tel_1,
                fax=user_profile.fax,
                zip=user_profile.zip,
                prefecture=user_profile.prefecture,
                city=user_profile.city,
                address_1=user_profile.address_1,
                address_2=user_profile.address_2,
                email_1=user_profile.email_1,
                email_2=user_profile.email_2,
                sex=user_profile.sex,
                birthday=user_profile.birthday
                )
        else:
            data = {}
        # xxx:ゆるふわなデフォルト値
        if data.get('sex') is None:
            data['sex'] = SexEnum.Female.v
        if data.get('birthday') is None:
            data['birthday'] = date(1980,1,1)

    client_form = get_base_form(request)
    form = client_form(
        context=context,
        flavors=flavors,
        _fields=fields,
        _data=data,
        formdata=formdata,
        **kwds)
    if form.country:
        form.country.choices = [(h, h) for h in Cart_ClientFormFactory(request).get_countries()]

    return form

def get_base_form(request):
    client_form = ClientFormFactory(request).make_form()
    return client_form
