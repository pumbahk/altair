# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
import sqlalchemy as sa
from altaircms.security import RootFactory
from altaircms.plugins.base.mixins import HandleSessionMixin
from altaircms.plugins.base.mixins import UpdateDataMixin
from altaircms.widget.models import AssetWidgetResourceMixin
from altaircms.asset.models import ImageAsset
from altaircms.modelmanager.repository import (
    AssetRepository, 
    WidgetRepository
)
from pyramid.decorator import reify
from . import forms
from .models import ImageWidget
from altaircms.asset.creation import ImageSearcher
from altaircms.tag.manager import MatchedTagNotFound

class FetchService(object):
    def __init__(self, context):
        self.context = context

    def try_form(self, params, FailureException):
        form = forms.FetchImageForm(params)
        if not form.validate():
            logger.warn(form.errors)
            raise FailureException()
        return form

    def get_assets_list(self, widget, page=0):
        return self.context.asset_repository.list_of_asset(widget.asset_id, page)

    def max_of_pages(self, widget):
        return self.context.asset_repository.count_of_asset(widget.asset_id)


class SearchService(object):
    def __init__(self, context):
        self.context = context

    def try_form(self, params, FailureException):
        form = forms.SearchByNameForm(params)
        if not form.validate():
            logger.warn(form.errors)
            raise FailureException()
        return form

    def _get_asset_query(self, widget, search_word):
        assets = self.context.asset_repository
        if search_word:
            assets = assets.filter(assets.Model.title.like(u"%{word}%".format(word=search_word)))
        return assets

    def get_assets_list(self, widget, search_word, page=0):
        assets = self._get_asset_query(widget, search_word)
        return assets.list_of_asset(widget.asset_id, page) #pagination

    def max_of_pages(self, widget, search_word):
        assets = self._get_asset_query(widget, search_word)        
        return assets.count_of_asset(widget.asset_id)

class TagsearchService(object):
    def __init__(self, context):
        self.context = context

    def try_form(self, params, FailureException):
        form = forms.SearchByTagForm(params)
        if not form.validate():
            logger.warn(form.errors)
            raise FailureException()
        return form

    def _get_asset_query(self, widget, search_word, FailureException):
        repository = self.context.asset_repository
        try:
            searcher = ImageSearcher(self.context.request, not_found_then_return_all=False)
            assets = searcher.search(repository._get_query(), {'tags':search_word}) #xxx:
            return repository.start_from(assets)
        except MatchedTagNotFound, e:
            logger.warn("matched tag is not found. search_word={word}".format(word=search_word))
            return repository.start_from(repository.Model.query.filter_by(id=-1))
        except Exception, e:
            logger.exception(e.message.encode("utf-8"))
            raise FailureException()

    def get_assets_list(self, widget, search_word, FailureException, page=0):
        assets = self._get_asset_query(widget, search_word, FailureException)
        return assets.list_of_asset(widget.asset_id, page) #pagination

    def max_of_pages(self, widget, search_word, FailureException):
        assets = self._get_asset_query(widget, search_word, FailureException)
        return assets.count_of_asset(widget.asset_id)

class ImageWidgetResource(HandleSessionMixin, #todo:remove
                          UpdateDataMixin, #todo:remove
                          AssetWidgetResourceMixin,  #todo:remove
                          RootFactory
                          ):
    WidgetClass = ImageWidget #todo:remove
    AssetClass = ImageAsset #todo:remove
    @reify
    def asset_repository(self):
        return AssetRepository(self.request, ImageAsset, offset=5).order_by(sa.desc(ImageAsset.updated_at))
    @reify
    def widget_repository(self):
        return WidgetRepository(self.request, ImageWidget)

    @reify
    def fetch_service(self):
        return FetchService(self)
    @reify
    def search_service(self):
        return SearchService(self)
    @reify
    def tagsearch_service(self):
        return TagsearchService(self)
