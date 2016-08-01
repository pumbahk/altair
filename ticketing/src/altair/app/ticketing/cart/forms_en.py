# -*- coding:utf-8 -*-
from altair.formhelpers.translations import Translations
from altair.formhelpers.form import OurForm, OurDynamicForm
from wtforms.validators import Regexp, Length, Optional, EqualTo, Email, AnyOf
from altair.formhelpers.validators import (
    Required,
    Phone,
    SejCompliantEmail,
    SwitchOptional,
    DynSwitchDisabled,
    )
from altair.formhelpers.fields.core import (
    OurTextField,
    OurRadioField,
    OurBooleanField,
    OurSelectField,
    OurIntegerField,
    OurFormField,
    )
from altair.formhelpers.fields.liaison import (
    Liaison,
    )
from altair.formhelpers.filters import (
    strip_spaces,
    ignore_space_hyphen,
    text_type_but_none_if_not_given,
    NFKC,
    lstrip,
    )

countries = [
    u'Japan',
    u'Algeria', u'Angola', u'Armenia', u'Azerbaijan', u'Australia', u'Albania', u'Austria', u'Anguilla', u'Antigua & Barbuda', u'Argentina',
    u'Bahrain', u'Benin', u'Botswana', u'Burkina-Faso', u'Bhutan', u'Brunei Darussalam', u'Belarus', u'Belgium', u'Bulgaria', u'Bahamas', u'Barbados', u'Belize', u'Bermuda', u'Bolivia', u'Brazil',
    u'Cape Verde', u'Chad', u'Congo (Republic of)', u'Cambodia', u'China', u'Croatia', u'Czech Republic', u'Cyprus', u'Cayman Islands', u'Chile', u'Colombia', u'Costa Rica', u'Canada',
    u'Dominica', u'Dominicana',
    u'Germany',
    u'Egypt', u'Estonia', u'Ecuador', u'EI Salvador',
    u'Fiji', u'France', u'Finland',
    u'Gambia', u'Ghana', u'Guinea-Bissau', u'Greece', u'Grenada', u'Guatemala', u'Guyana',
    u'Hong Kong', u'Hungary', u'Honduras',
    u'India', u'Israel', u'Indonesia', u'Iceland', u'Ireland', u'Italy',
    u'Jordan', u'Jamaica',
    u'Kenya', u'Kuwait', u'Kazakstan', u'Korea', u'Kyrgyzstan',
    u'Liberia', u'Laos', u'Lebanon', u'Latvia', u'Lithuania', u'Luxemburg',
    u'Madagascar', u'Malawi', u'Mali', u'Mauritania', u'Mauritius', u'Mozambique', u'Macau', u'Malaysia', u'Micronesia, Fed States Of', u'Mongolia', u'Macedonia', u'Malta', u'Moldova', u'Mexico', u'Montrserrat',
    u'Namibia', u'Niger', u'Nigeria', u'Nepal', u'New Zealand', u'Netherlands', u'Norway', u'Nicaragua',
    u'Oman', u'Qatar',
    u'Pakistan', u'Palau', u'Papua New Guinea', u'Philippines', u'Polska', u'Portugal', u'Panama', u'Paraguay', u'Peru',
    u'Romania', u'Russia',
    u'Sao Tome e Principe', u'Saudi Arabia', u'Senegal', u'Seychelles', u'Sierra Leone', u'South Africa', u'Swaziland', u'Singapore', u'Solomon Islands', u'Sri Lanka', u'Spain', u'Switzerland', u'Slovakia', u'Slovenia', u'Sweden', u'Saint Kitts & Nevis', u'Saint Lucia', u'Saint Vincent & The Grenadines', u'Suriname',
    u'Tanzania', u'Tunisia', u'Taiwan', u'Tajikistan', u'Thailand', u'Turkmenistan', u'Turkey', u'Trinidad & Tobago', u'Turks & Caicos',
    u'Uganda', u'United Arab Emirates', u'Uzbekistan', u'UK', u'Uruguay', u'USA',
    u'Vietnam', u'Venezuela', u'Virgin Islands, British',
    u'Yemen',
    u'Zimbabwe'
]

length_limit_for_sej_en = Length(max=20, message=u'20文字以内で入力してください')
class ClientForm(OurDynamicForm):
    """国際化の英語フォーム"""
    def _get_translations(self):
        return Translations()

    last_name = OurTextField(
        label=u"Last name",
        filters=[strip_spaces],
        validators=[
            Required(u'Please input.'),
            length_limit_for_sej_en,
            ],
        )
    first_name = OurTextField(
        label=u"First name",
        filters=[strip_spaces],
        validators=[
            Required(u'Please input.'),
            length_limit_for_sej_en,
            ]
        )
    tel_1 = OurTextField(
        label=u"Phone number",
        filters=[ignore_space_hyphen, NFKC],
        validators=[
            SwitchOptional('tel_2'),
            Required(u'Please input.'),
            Length(min=1, max=11),
            Regexp(r'^\d*$', message=u'Please enter the only single-byte numbers disconnect the (hyphen)'),
            ]
        )
    tel_2 = OurTextField(
        label=u"Phone number 2",
        filters=[ignore_space_hyphen, NFKC],
        validators=[
            Optional(),
            Length(min=1, max=11),
            Regexp(r'^\d*$', message=u'Please enter the only single-byte numbers disconnect the (hyphen)'),
            ]
        )
    fax = OurTextField(
        label=u"FAX",
        filters=[ignore_space_hyphen, NFKC],
        validators=[
            Optional(),
            Length(min=1, max=11),
            Phone(u'Check fax number, please.'),
            ]
        )
    zip = OurTextField(
        label=u"Zip",
        filters=[ignore_space_hyphen, NFKC],
        validators=[
            Optional(),
            Regexp(r'^\d{7}$', message=u'Please enter the only single-byte numbers disconnect the (hyphen) (7 digits)'),
            Length(min=7, max=7, message=u'Please check'),
            ]
        )
    country = OurSelectField(
        label=u"Country/Area",
        filters=[strip_spaces],
        validators=[
            Required(u'Please input.'),
            AnyOf(countries, message=u"Invalid value, can't be any of: %(countries)s")
            ]
        )
    prefecture = OurTextField(
        label=u"State/Province/Region",
        filters=[strip_spaces],
        validators=[
            Required(u'Please input.'),
            ]
        )
    city = OurTextField(
        label=u"City",
        filters=[strip_spaces],
        validators=[
            Required(u'Please input.'),
            Length(max=255, message=u'Please enter up to 255 characters'),
        ]
    )
    address_1 = OurTextField(
        label=u"Address 1",
        filters=[strip_spaces],
        validators=[
            Required(u'Please input.'),
            Length(max=255, message=u'Please enter up to 255 characters'),
            ]
        )
    address_2 = OurTextField(
        label=u"Address 2",
        filters=[strip_spaces],
        validators=[
            Length(max=255, message=u'Please enter up to 255 characters'),
            ]
        )
    email_1 = OurTextField(
        label=u"Email",
        filters=[strip_spaces, NFKC],
        description=lambda field: field._form.context.request.view_context.mail_filter_domain_notice if hasattr(field._form.context.request, 'view_context') else u'',
        validators=[
            Required(u'Please input.'),
            Email(u'Please input right format email'),
            ]
        )
    email_1_confirm = OurTextField(
        label=u"Confirmation",
        filters=[strip_spaces, NFKC],
        validators=[
            Required(u'Please input.'),
            Email(u'Please input right format email'),
            ]
        )
    email_2 = Liaison(
        email_1,
        OurTextField(
            label=u"Email",
            filters=[strip_spaces, NFKC],
            validators=[
                SejCompliantEmail(),
                ]
            )
        )
    email_2_confirm = Liaison(
        email_1_confirm,
        OurTextField(
            label=u"Confirmation",
            filters=[strip_spaces, NFKC],
            validators=[
                SejCompliantEmail(),
                ]
            )
        )

    def __init__(self, formdata=None, obj=None, prefix=u'', **kwargs):
        context = kwargs.pop('context')
        self.context = context
        flavors = kwargs.pop('flavors', {})
        super(ClientForm, self).__init__(formdata, obj, prefix, **kwargs)
        if flavors.get('japanese_prefectures', False):
            self.prefecture.widget = japanese_prefecture_select_input

    def validate_tel_2(self, field):
        if not self.tel_1.data and not self.tel_2.data:
            raise ValidationError(u'Telephone number, please enter either or mobile or home')

    def _validate_email_addresses(self, *args, **kwargs):
        status = True
        data = self.data
        if data["email_1"] != data["email_1_confirm"]:
            getattr(self, "email_1").errors.append(u"E-mail address and the confirmation email address does not match")
            status = False
        if data["email_2"] != data["email_2_confirm"]:
            getattr(self, "email_2").errors.append(u"E-mail address and the confirmation email address does not match")
            status = False
        return status

    def validate(self):
        status = super(ClientForm, self).validate()
        status = self._validate_email_addresses() and status
        return status
