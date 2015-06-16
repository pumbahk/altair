from zope.interface import Interface, Attribute

class IFamiPortEndpoints(Interface):
    endpoint_base = Attribute('')
    inquiry = Attribute('')
    payment = Attribute('')
    completion = Attribute('')
    cancel = Attribute('')
    information = Attribute('')
    customer = Attribute('')
    refund = Attribute('')

class IFamiPortCommunicator(Interface):
    def fetch_information(type, store_code, client_code, event_code_1, event_code_2, performance_code, sales_segment_code, reserve_number, auth_number):
        pass

class IFamiPortClientConfiguration(Interface):
    code = Attribute('')
    auth_number_required = Attribute('')

class IFamiPortClientConfigurationRegistry(Interface):
    def lookup(code):
        pass

    def __iter__():
        pass
