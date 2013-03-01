from ..modelmanager.interfaces import IPublishingModelSearcher as ITopicSearcher

def get_topic_searcher(request, topic_type):
    return request.registry.queryUtility(ITopicSearcher, name=topic_type)(request)
