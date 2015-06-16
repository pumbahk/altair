from .interfaces import IFamiPortCommunicator, IFamiPortClientConfigurationRegistry, IMmkSequence

def get_communicator(request):
    return request.registry.queryUtility(IFamiPortCommunicator)

def get_client_configuration_registry(request):
    return request.registry.queryUtility(IFamiPortClientConfigurationRegistry)

def get_mmk_sequence(request):
    return request.registry.queryUtility(IMmkSequence)
