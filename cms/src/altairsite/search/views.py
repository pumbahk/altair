# -*- coding:utf-8 -*-
from pyramid.view import view_config
from pyramid.view import view_defaults
from altaircms.tag.models import HotWord
from altaircms.models import SalesSegmentKind
from altaircms.page.models import PageTag
from webob.multidict import MultiDict
from pyramid.httpexceptions import HTTPNotFound
import logging
import sqlalchemy.orm as orm
from . import forms
from . import searcher

logger = logging.getLogger(__file__)

def enable_search_function(info, request):
    return request.organization.use_full_usersite if request.organization else False

@view_config(custom_predicates=(enable_search_function, ), 
             route_name="page_search_input", renderer="altaircms:templates/usersite/search/input.html")
def page_search_input(request):
    """ 絞り込み検索フォーム画面
    """
    request.body_id = "searchform"
    return {"forms": forms.get_search_forms(request)}

@view_config(custom_predicates=(enable_search_function, ), 
             route_name="page_search_result", renderer="altaircms:templates/usersite/search/result.html")
def page_search_result(context, request):
    """ 詳細検索 検索結果
    """
    try:
        request.body_id = "search"
        logger.debug("search GET params: %s" % request.GET)
        query_params = forms.get_search_forms(request, request.GET).make_query_params()
        result_seq = context.get_result_sequence_from_query_params(
            query_params, 
            searchfn=searcher.get_pageset_query_fullset
            )
        html_query_params = context.get_query_params_as_html(query_params)
        return dict(result_seq=result_seq, query_params=html_query_params)
    except Exception, e:
        logger.exception(e)
        raise HTTPNotFound

@view_config(custom_predicates=(enable_search_function, ), 
             request_param="q", route_name="page_search_by_freeword", 
             renderer="altaircms:templates/usersite/search/result.html")
def search_by_freeword(context, request):
    """ フリーワード検索
    """
    try:
        ## 全文検索を使って検索。, で区切られた文字はandで結合
        request.body_id = "search"
        query_params = dict(query=request.GET.get("q", u""), query_cond="intersection")

        result_seq = context.get_result_sequence_from_query_params(
            query_params,
            searchfn=searcher.get_pageset_query_from_freeword
            )
        ## query_paramsをhtml化する
        html_query_params = context.get_query_params_as_html(query_params)
        return dict(result_seq=result_seq, query_params=html_query_params)
    except Exception, e:
        logger.exception(e)
        raise HTTPNotFound


@view_config(custom_predicates=(enable_search_function, ), 
             route_name="page_search_by_multi", 
             renderer="altaircms:templates/usersite/search/result.html")
def search_by_multi(request):
    """ topページの複数記入できるフォーム。
    """
    try:
        logger.debug("search GET params: %s" % request.GET)
        request.body_id = "search"
        query_params = forms.TopPageSidebarSearchForm(request.GET).make_query_params()
        result_seq = request.context.get_result_sequence_from_query_params(
            query_params, 
            searchfn=searcher.get_pageset_query_from_multi
            )
        html_query_params = request.context.get_query_params_as_html(query_params)
        return dict(result_seq=result_seq, query_params=html_query_params)

    except Exception, e:
        logger.exception(e)
        raise HTTPNotFound


@view_defaults(custom_predicates=(enable_search_function, ), 
               route_name="page_search_by", renderer="altaircms:templates/usersite/search/result.html")
class SearchByKindView(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context

    @view_config(match_param="kind=genre") #kind, value
    def search_by_genre(self):
        """ ジャンルで検索
        """
        try:
            params = MultiDict({"top": self.request.matchdict["value"], "sub": self.request.matchdict["value"]})
            self.request.body_id = "search"
            query_params = forms.GenrePartForm(params).configure(self.request).make_query_params()

            result_seq = self.context.get_result_sequence_from_query_params(
                query_params,
                searchfn=searcher.get_pageset_query_from_genre
                )
            ## query_paramsをhtml化する
            html_query_params = self.context.get_query_params_as_html(query_params)
            ### header page用のcategoryを集めてくる
            return dict(result_seq=result_seq, query_params=html_query_params)
        except Exception, e:
            logger.exception(e)
            raise HTTPNotFound

    @view_config(match_param="kind=area") #kind, value
    def search_by_area(self):
        """ エリアで検索した結果を表示
        """
        try:
            params = MultiDict({self.request.matchdict["value"]: "on"})
            self.request.body_id = "search"
            query_params = forms.AreaPartForm(params).make_query_params()
            
            result_seq = self.context.get_result_sequence_from_query_params_ext(
                query_params,
                searchfn=searcher.get_pageset_query_from_area
                )
            ## query_paramsをhtml化する
            html_query_params = self.context.get_query_params_as_html(query_params)
            ### header page用のcategoryを集めてくる
            return dict(result_seq=result_seq, query_params=html_query_params)
        except Exception, e:
            logger.exception(e)
            raise HTTPNotFound

    @view_config(match_param="kind=deal_cond") #kind, value
    def search_by_deal_cond(self):
        """ 販売条件で検索した結果を表示
        """
        try:
            kind = self.request.allowable(SalesSegmentKind).filter_by(name=self.request.matchdict["value"]).first()
            if kind is None:
                raise HTTPNotFound("not found")
            params = MultiDict({"deal_cond": unicode(kind.id)})
            self.request.body_id = "search"
            query_params = forms.DealCondPartForm(params).configure(self.request).make_query_params()
            result_seq = self.context.get_result_sequence_from_query_params_ext(
                query_params,
                searchfn=searcher.get_pageset_query_from_deal_cond
                )
            ## query_paramsをhtml化する
            html_query_params = self.context.get_query_params_as_html(query_params)
            ### header page用のcategoryを集めてくる
            return dict(result_seq=result_seq, query_params=html_query_params)
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
            self.request.body_id = "search"
            query_params = {"ndays": n, 
                            "query_expr_message": u"%d日以内に公演" % n}
            result_seq = self.context.get_result_sequence_from_query_params_ext(
                query_params,
                searchfn=searcher.get_pageset_query_from_event_open_within
                )

            ## query_paramsをhtml化する
            html_query_params = self.context.get_query_params_as_html(query_params)
            ### header page用のcategoryを集めてくる
            return dict(result_seq=result_seq, query_params=html_query_params)
        except Exception, e:
            logger.exception(e)
            raise HTTPNotFound

    @view_config(match_param="kind=deal_open") #kind, value
    def search_by_deal_open(self):
        """ 販売条件で検索した結果を表示
        """
        try:
            n = int(self.request.matchdict["value"])
            self.request.body_id = "search"
            query_params = {"ndays": n, 
                            "query_expr_message": u"%d日以内に受付・発売開始" % n}
            result_seq = self.context.get_result_sequence_from_query_params_ext(
                query_params,
                searchfn=searcher.get_pageset_query_from_deal_open_within
                )
            ## query_paramsをhtml化する

            html_query_params = self.context.get_query_params_as_html(query_params)
            ### header page用のcategoryを集めてくる
            return dict(result_seq=result_seq, query_params=html_query_params)
        except Exception, e:
            logger.exception(e)
            raise HTTPNotFound

    @view_config(match_param="kind=hotword") #kind, value
    def search_by_hotword(self):
        """ ホットワードの飛び先
        """
        try:
            hotword_id = self.request.matchdict["value"]
            hotword = self.request.allowable(HotWord).filter(HotWord.id==hotword_id, HotWord.enablep == True)
            hotword = hotword.options(orm.joinedload("tag")).first()
            if hotword is None:
                logger.warn("hot word is not found" % hotword_id)
            self.request.body_id = "search"
            query_params = {"hotword": hotword, 
                            "query_expr_message": u"ホットワード:%s" % hotword.name}
            result_seq = self.context.get_result_sequence_from_query_params(
                query_params,
                searchfn=searcher.get_pageset_query_from_hotword
                )
            ## query_paramsをhtml化する

            html_query_params = self.context.get_query_params_as_html(query_params)
            ### header page用のcategoryを集めてくる
            return dict(result_seq=result_seq, query_params=html_query_params)
        except Exception, e:
            logger.exception(e)
            raise HTTPNotFound

    @view_config(match_param="kind=pagetag") #kind, value
    def search_by_pagetag(self):
        """ ホットワードの飛び先
        """
        try:
            pagetag_id = self.request.matchdict["value"]
            pagetag = self.request.allowable(PageTag).filter(PageTag.id==pagetag_id, PageTag.publicp==True).first()
            if pagetag is None:
                logger.warn("page tag is not found" % pagetag_id)
            self.request.body_id = "search"
            query_params = {"pagetag": pagetag, 
                            "query_expr_message": pagetag.label}
            result_seq = self.context.get_result_sequence_from_query_params(
                query_params,
                searchfn=searcher.get_pageset_query_from_pagetag
                )
            ## query_paramsをhtml化する

            html_query_params = self.context.get_query_params_as_html(query_params)
            ### header page用のcategoryを集めてくる
            return dict(result_seq=result_seq, query_params=html_query_params)
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
        self.request.body_id = "search"
        result_seq = self.context.get_result_sequence_from_query_params(
            mock_query_parms, 
            )
        ### header page用のcategoryを集めてくる
        return dict(result_seq=result_seq, query_params=html_query_params)
