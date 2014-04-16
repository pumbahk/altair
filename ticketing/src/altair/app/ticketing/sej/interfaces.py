from zope.interface import Interface, Attribute

class ISejTenant(Interface):
    shop_name               = Attribute("")
    shop_id                 = Attribute("")
    contact_01              = Attribute("")
    contact_02              = Attribute("")
    api_key                 = Attribute("")
    inticket_api_url        = Attribute("")
