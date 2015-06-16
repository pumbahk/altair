from .interfaces import IFamiPortCommunicator

def get_communicator(request):
    return request.registry.queryUtility(IFamiPortCommunicator)
