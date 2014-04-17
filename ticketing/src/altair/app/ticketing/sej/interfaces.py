from zope.interface import Interface, Attribute

class ISejTenant(Interface):
    shop_name               = Attribute("")
    shop_id                 = Attribute("")
    contact_01              = Attribute("")
    contact_02              = Attribute("")
    api_key                 = Attribute("")
    inticket_api_url        = Attribute("")

class ISejPaymentAPICommunicator(Interface):
    def request_file(params, retry_mode):
        pass

    def request(params, retry_mode):
        pass

class ISejPaymentAPICommunicatorFactory(Interface):
    def __call__(tenant, path):
        pass
