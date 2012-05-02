from .interfaces import IFulltextSearch

def add_fulltext_search(config, search_utility):
    if isinstance(search_utility, basestring):
        search_utility = config.maybe_dotted(search_utility)


    registry = config.registry
    registry.registerUtility(search_utility, IFulltextSearch)


