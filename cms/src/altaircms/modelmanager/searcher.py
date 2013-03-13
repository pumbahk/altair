import functools
from pyramid.decorator import reify
from altaircms.tag.api import get_tagmanager
from altaircms.tag.api import get_system_tagmanager

from pyramid.config import ConfigurationError
from .interfaces import IPublishingModelSearcher

class PublishingModelSearcher(object):
    def __init__(self, TargetModel, request):
        self.TargetModel = TargetModel
        assert TargetModel.type
        self.type = TargetModel.type
        self.request = request

    @classmethod
    def register(cls, config, TargetModel):
        if not hasattr(TargetModel, "publishing"):
            raise ConfigurationError("%s doesn't have 'publishing' method." % TargetModel)  
        if not hasattr(TargetModel, "type"):
            raise ConfigurationError("%s doesn't have 'type' attribute" % TargetModel)  
        config.registry.registerUtility(functools.partial(cls, TargetModel),
                                        IPublishingModelSearcher, name=TargetModel.type)
        
    @reify
    def tagmanager(self):
        return get_tagmanager(self.type, request=self.request)

    @reify
    def system_tagmanager(self):
        return get_system_tagmanager(self.type, request=self.request)

    def _start_query(self):
        if hasattr(self.request, "allowable"):
            return self.request.allowable(self.TargetModel)
        else:
            return self.TargetModel.query

    def query_publishing_no_filtered(self, dt, qs=None):
        qs = qs or self._start_query()
        return self.TargetModel.publishing(d=dt, qs=qs)

    def filter_by_tag(self, qs, tag):
        return self.tagmanager.more_filter_by_tag(qs, tag)

    def filter_by_system_tag(self, qs, tag):
        return self.system_tagmanager.more_filter_by_tag(qs, tag)

    def filter_by_genre_label(self, qs, genre_label):
        system_tag = self.get_tag_from_genre_label(genre_label)
        return self.system_tagmanager.more_filter_by_tag(qs, system_tag)

    def get_tag_from_genre_label(self, genre_label):
        return self.system_tagmanager.get_or_create_tag(genre_label, public_status=True)

    def query_publishing(self, dt, tag, system_tag=None): #system_tag is tag
        qs = self.query_publishing_no_filtered(dt)
        qs = self.filter_by_tag(qs, tag)
        
        if system_tag:
            qs = self.filter_by_system_tag(qs, system_tag)
        return qs

    def filter_by_tag_many(self, qs, tags): #distinct
        return self.tagmanager.more_filter_by_tag(qs, tags)

    def filter_by_system_tag_many(self, qs, tags): #distinct
        return self.system_tagmanager.more_filter_by_tag_many(qs, tags)

    def query_publishing_many(self, dt, tags, system_tags=[]):
        qs = self.query_publishing_no_filtered(dt)
        qs = self.filter_by_tags(qs, tags)

        if system_tags:
            qs = self.filter_by_system_tags(qs, system_tags)
        return qs
