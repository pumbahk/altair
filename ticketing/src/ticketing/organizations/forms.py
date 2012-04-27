# -*- coding: utf-8 -*-

from deform.widget import SelectWidget
from colander import MappingSchema, SchemaNode, String, Int, DateTime
from ticketing.master.models import Prefecture

class OrganizationForm(MappingSchema):
    name            = SchemaNode(String()   , title=u'クライアント名')
    contract_type     = SchemaNode(Int()      , title=u'クライアントタイプ'
                                 , widget= SelectWidget(values=[(1, u'スタンダード')]))
    company_name    = SchemaNode(String()   , title=u'会社名')
    section_name    = SchemaNode(String()   , title=u'部署名')
    zip_code        = SchemaNode(String()   , title=u'郵便番号')
    country_code    = SchemaNode(String()   , title=u'国'
                                 , widget= SelectWidget(values=[(81, u'日本')]))
    prefecture_code = SchemaNode(String()   , title=u'都道府県'
                                 , widget= SelectWidget(values=[(pref.id, pref.name) for pref in Prefecture.all()]))
    city            = SchemaNode(String()   , title=u'市町村区')
    address         = SchemaNode(String()   , title=u'町名')
    street          = SchemaNode(String()   , title=u'番地')
    other_address   = SchemaNode(String()   , title=u'アパート・マンション名')
    company_name    = SchemaNode(String()   , title=u'会社名')
    section_name    = SchemaNode(String()   , title=u'部署名')
    tel_1           = SchemaNode(String()   , title=u'電話番号')
    tel_2           = SchemaNode(String()   , title=u'携帯電話番号')
    fax             = SchemaNode(String()   , title=u'FAX番号')
