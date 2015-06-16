from .interfaces import IFamiPortCommunicator, IFamiPortClientConfigurationRegistry

def get_communicator(request):
    return request.registry.queryUtility(IFamiPortCommunicator)

def get_client_configuration_registry(request):
    return request.registry.queryUtility(IFamiPortClientConfigurationRegistry)
