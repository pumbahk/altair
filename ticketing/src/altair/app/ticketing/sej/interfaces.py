from zope.interface import Interface, Attribute

class ISejNWTSInfo(Interface):
    nwts_endpoint_url       = Attribute("")
    nwts_terminal_id        = Attribute("")
    nwts_password           = Attribute("")

class ISejTenant(ISejNWTSInfo):
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

class ISejTicketTemplateRecord(Interface):
    status                  = Attribute('''''') 
    template_id             = Attribute('''''') 
    template_name           = Attribute('''''') 
    ticket_html             = Attribute('''''') 
    ticket_css              = Attribute('''''') 
    publish_start_date      = Attribute('''''') 
    publish_end_date        = Attribute('''''') 
    sent_at                 = Attribute('''''') 

class ISejNWTSUploaderFactory(Interface):
    def __call__(endpoint_url, terminal_id, password):
        pass

class ISejNWTSUploader(Interface):
    def __call__(application, file_id, data):
        pass

