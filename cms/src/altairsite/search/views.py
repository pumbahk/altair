# -*- coding:utf-8 -*-
from pyramid.view import view_config
from pyramid.view import view_defaults
from webob.multidict import MultiDict
from pyramid.httpexceptions import HTTPNotFound
import logging

from ..front import api as front_api
from . import forms
from . import searcher

logger = logging.getLogger(__file__)

@view_config(route_name="page_search_input", renderer="altaircms:templates/front/layout/ticketstar.search.input.mako")
def page_search_input(request):
    """ 絞り込み検索フォーム画面
    """
    params = front_api.get_navigation_categories(request)
    params.update(forms=forms.get_search_forms())
    return params

@view_config(route_name="page_search_result", renderer="altaircms:templates/front/layout/ticketstar.search.mako")
def page_search_result(request):
    """ 詳細検索 検索結果
    """
    try:
        logger.debug("search GET params: %s" % request.GET)
        query_params = forms.get_search_forms(request.GET).make_query_params()
        result_seq = request.context.get_result_sequence_from_query_params(
            query_params, 
            searchfn=searcher.get_pageset_query_fullset
            )
        html_query_params = request.context.get_query_params_as_html(query_params)

        params = front_api.get_navigation_categories(request)
        params.update(result_seq=result_seq, query_params=html_query_params)
        return params
    except Exception, e:
        logger.exception(e)
        raise HTTPNotFound

@view_config(request_param="q", route_name="page_search_by_freeword", 
             renderer="altaircms:templates/front/layout/ticketstar.search.mako")
def search_by_freeword(context, request):
    """ フリーワード検索
    """
    try:
        ## 全文検索を使って検索。, で区切られた文字はandで結合
        query_params = dict(query=request.GET.get("q", u""), query_cond="intersection")

        result_seq = context.get_result_sequence_from_query_params(
            query_params,
            searchfn=searcher.get_pageset_query_from_freeword
            )
        ## query_paramsをhtml化する
        html_query_params = context.get_query_params_as_html(query_params)
        ### header page用のcategoryを集めてくる
        params = front_api.get_navigation_categories(request)
        params.update(result_seq=result_seq, query_params=html_query_params)
        return params
    except Exception, e:
        logger.exception(e)
        raise HTTPNotFound


@view_config(route_name="page_search_by_multi", 
             renderer="altaircms:templates/front/layout/ticketstar.search.mako")
def search_by_multi(request):
    """ topページの複数記入できるフォーム。
    """
    try:
        logger.debug("search GET params: %s" % request.GET)
        query_params = forms.TopPageSidebarSearchForm(request.GET).make_query_params()
        result_seq = request.context.get_result_sequence_from_query_params(
            query_params, 
            searchfn=searcher.get_pageset_query_from_multi
            )
        html_query_params = request.context.get_query_params_as_html(query_params)

        params = front_api.get_navigation_categories(request)
        params.update(result_seq=result_seq, query_params=html_query_params)
        return params
    except Exception, e:
        logger.exception(e)
        raise HTTPNotFound


@view_defaults(route_name="page_search_by", renderer="altaircms:templates/front/layout/ticketstar.search.mako")
class SearchByKindView(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context

    @view_config(match_param="kind=genre") #kind, value
    def search_by_genre(self):
        """ ジャンルで検索
        """
        try:
            params = MultiDict({self.request.matchdict["value"]: "on"})
            query_params = forms.GenrePartForm(params).make_query_params()

            result_seq = self.context.get_result_sequence_from_query_params(
                query_params,
                searchfn=searcher.get_pageset_query_from_genre
                )
            ## query_paramsをhtml化する
            html_query_params = self.context.get_query_params_as_html(query_params)
            ### header page用のcategoryを集めてくる
            params = front_api.get_navigation_categories(self.request)
            params.update(result_seq=result_seq, query_params=html_query_params)
            return params
        except Exception, e:
            logger.exception(e)
            raise HTTPNotFound

    @view_config(match_param="kind=area") #kind, value
    def search_by_area(self):
        """ エリアで検索した結果を表示
        """
        try:
            params = MultiDict({self.request.matchdict["value"]: "on"})
            query_params = forms.AreaPartForm(params).make_query_params()

            result_seq = self.context.get_result_sequence_from_query_params(
                query_params,
                searchfn=searcher.get_pageset_query_from_area
                )
            ## query_paramsをhtml化する
            html_query_params = self.context.get_query_params_as_html(query_params)
            ### header page用のcategoryを集めてくる
            params = front_api.get_navigation_categories(self.request)
            params.update(result_seq=result_seq, query_params=html_query_params)
            return params
        except Exception, e:
            logger.exception(e)
            raise HTTPNotFound

    @view_config(match_param="kind=deal_cond") #kind, value
    def search_by_deal_cond(self):
        """ 販売条件で検索した結果を表示
        """
        try:
            params = MultiDict({self.request.matchdict["value"]: True})
            query_params = forms.DealCondPartForm(params).make_query_params()
            result_seq = self.context.get_result_sequence_from_query_params(
                query_params,
                searchfn=searcher.get_pageset_query_from_deal_cond
                )
            ## query_paramsをhtml化する
            html_query_params = self.context.get_query_params_as_html(query_params)
            ### header page用のcategoryを集めてくる
            params = front_api.get_navigation_categories(self.request)
            params.update(result_seq=result_seq, query_params=html_query_params)
            return params
        except Exception, e:
            logger.exception(e)
            raise HTTPNotFound

    @view_config(match_param="kind=event_open") #kind, value
    def search_by_event_open(self):
        """ 公演期間で検索した結果を表示
        **N日以内に公演**
        """
        try:
            n = int(self.request.matchdict["value"])
            query_params = {"ndays": n, 
                            "query_expr_message": u"%d日以内に公演" % n}
            result_seq = self.context.get_result_sequence_from_query_params(
                query_params,
                searchfn=searcher.get_pageset_query_from_event_open_within
                )

            ## query_paramsをhtml化する
            html_query_params = self.context.get_query_params_as_html(query_params)
            ### header page用のcategoryを集めてくる
            params = front_api.get_navigation_categories(self.request)
            params.update(result_seq=result_seq, query_params=html_query_params)
            return params
        except Exception, e:
            logger.exception(e)
            raise HTTPNotFound

    @view_config(match_param="kind=deal_open") #kind, value
    def search_by_deal_open(self):
        """ 販売条件で検索した結果を表示
        """
        try:
            n = int(self.request.matchdict["value"])
            query_params = {"ndays": n, 
                            "query_expr_message": u"%d日以内に受付・発売開始" % n}
            result_seq = self.context.get_result_sequence_from_query_params(
                query_params,
                searchfn=searcher.get_pageset_query_from_deal_open_within
                )
            ## query_paramsをhtml化する

            html_query_params = self.context.get_query_params_as_html(query_params)
            ### header page用のcategoryを集めてくる
            params = front_api.get_navigation_categories(self.request)
            params.update(result_seq=result_seq, query_params=html_query_params)
            return params
        except Exception, e:
            logger.exception(e)
            raise HTTPNotFound

    @view_config(match_param="kind=hotword") #kind, value
    def search_by_hotword(self):
        """ ホットワードの飛び先
        """
        try:
            hotword = self.request.matchdict["value"]
            query_params = {"hotword": hotword, 
                            "query_expr_message": u"ホットワード:%s" % hotword}
            result_seq = self.context.get_result_sequence_from_query_params(
                query_params,
                searchfn=searcher.get_pageset_query_from_hotword
                )
            ## query_paramsをhtml化する

            html_query_params = self.context.get_query_params_as_html(query_params)
            ### header page用のcategoryを集めてくる
            params = front_api.get_navigation_categories(self.request)
            params.update(result_seq=result_seq, query_params=html_query_params)
            return params
        except Exception, e:
            logger.exception(e)
            raise HTTPNotFound

    @view_config(match_param="kind=mock")
    def search_by_mock(self):
        """ mockup (for testing)
        """
        class mock_query_parms(object):
            @classmethod
            def __html__(cls):
                return "mock-dummy"
        html_query_params = mock_query_parms
        result_seq = self.context.get_result_sequence_from_query_params(
            mock_query_parms, 
            )
        ### header page用のcategoryを集めてくる
        params = front_api.get_navigation_categories(self.request)
        params.update(result_seq=result_seq, query_params=html_query_params)
        return params
