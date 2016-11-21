# -*- coding: utf-8 -*-
from datetime import datetime as dt
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
        metadata = getattr(request, 'altair_auth_metadata', {})
        if request.altair_auth_info['membership_source'] == 'altair.oauth_auth.plugin.OAuthAuthPlugin':
            metadata = metadata[u'profile']
        if context.membershipinfo is not None and context.membershipinfo.enable_auto_input_form:
            birthday = None
            if metadata.get('birthday'):
                birthday = dt.strptime(metadata.get('birthday'), '%Y-%m-%d').date()
            data = dict(
                last_name=metadata.get('last_name'),
                last_name_kana=metadata.get('last_name_kana'),
                first_name=metadata.get('first_name'),
                first_name_kana=metadata.get('first_name_kana'),
                tel_1=metadata.get('tel_1'),
                fax=metadata.get('fax'),
                zip=metadata.get('zip'),
                prefecture=metadata.get('prefecture'),
                city=metadata.get('city'),
                address_1=metadata.get('address_1'),
                address_2=metadata.get('address_2'),
                email_1=metadata.get('email_1'),
                email_2=metadata.get('email_2'),
                sex=metadata.get('sex'),
                birthday=birthday
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
    # emailアドレスが取れた場合は、確認用も埋めてしまう
    if form.email_1.data:
        form.email_1_confirm.data = form.email_1.data
    if form.country:
        form.country.choices = [(h, h) for h in Cart_ClientFormFactory(request).get_countries()]

    return form

def get_base_form(request):
    client_form = ClientFormFactory(request).make_form()
    return client_form
