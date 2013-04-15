# -*- coding: utf-8 -*-
from pyramid.view import view_config
from altaircms.models import Genre
from altairsite.mobile.event.search.forms import SearchForm
from altairsite.mobile.core.searcher import EventSearcher
from altairsite.mobile.core.const import get_prefecture_name
from altairsite.mobile.core.helper import exist_value, get_week_map, get_event_paging
from altairsite.mobile.core.helper import log_info
from altaircms.page.models import Page, PageSet, MobileTag, MobileTag2Page
from altaircms.event.models import Event
from .forms import MobileTagSearchForm

class ValidationFailure(Exception):
    pass

@view_config(route_name='search', request_type="altairsite.mobile.tweens.IMobileRequest"
    , renderer='altairsite.mobile:templates/searchresult/search.mako')
@view_config(route_name='genresearch', request_type="altairsite.mobile.tweens.IMobileRequest"
    , renderer='altairsite.mobile:templates/searchresult/genresearch.mako')
def search(request):

    log_info("search", "start")
    form = SearchForm(request.GET)
    form.num.data = 0
    form.week.data = get_week_map()
    searcher = EventSearcher(request)

    if (form.area.data and int(form.area.data) > 0) and (form.word.data is None or form.word.data == ""): # 地域検索
        log_info("search", "search event start(area)")
        if exist_value(form.genre.data): # ジャンル画面からの地域検索
            qs = searcher.get_events_from_freeword(form)
            if qs:
                qs = searcher.get_events_from_area(form, qs)
                qs = searcher.get_events_from_sale(form, qs)
        else: # トップ画面からの地域検索
            qs = searcher.get_events_from_area(form)
            qs = searcher.get_events_from_sale(form, qs)

        log_info("search", "search event end(area)")
        form = get_event_paging(request=request, form=form, qs=qs)
    else: # 検索文字列あり
        if form.validate():
            log_info("search", "search event start")
            qs = searcher.get_events_from_freeword(form)
            if qs:
                qs = searcher.get_events_from_area(form, qs)
                qs = searcher.get_events_from_sale(form, qs)
            log_info("search", "search event end")
            form = get_event_paging(request=request, form=form, qs=qs)

    # パンくずリスト用
    log_info("search", "breadcrumb create start")
    if exist_value(form.genre.data):
        form.navi_genre.data = request.allowable(Genre).filter(Genre.id==form.genre.data).first()

    if exist_value(form.sub_genre.data):
        form.navi_sub_genre.data = request.allowable(Genre).filter(Genre.id==form.sub_genre.data).first()

    if exist_value(form.area.data):
        form.navi_area.data = get_prefecture_name(form.area.data)
    log_info("search", "breadcrumb create end")

    log_info("search", "end")
    return {'form':form}

@view_config(route_name='mobile_tag_search', request_type="altairsite.mobile.tweens.IMobileRequest"
    , renderer='altairsite.mobile:templates/searchresult/mobile_tag_search_result.mako')
def mobile_tag_search(request):

    log_info("mobile_tag_search", "start")
    form = MobileTagSearchForm(request.GET)
    form.page.data = request.matchdict['page']
    form.week.data = get_week_map()

    mobile_tag_id = request.matchdict["mobile_tag_id"]
    mobile_tag = request.allowable(MobileTag).filter(MobileTag.id == mobile_tag_id).first()
    if not mobile_tag:
        log_info("mobile_tag_search", "mobile tag is not found")
        raise ValidationFailure

    qs = request.allowable(Event) \
        .filter(Event.is_searchable == True) \
        .join(PageSet, Event.id == PageSet.event_id) \
        .join(MobileTag2Page, PageSet.id == MobileTag2Page.object_id) \
        .join(MobileTag, MobileTag2Page.tag_id == MobileTag.id) \
        .filter(MobileTag.id == mobile_tag_id)

    form = get_event_paging(request=request, form=form, qs=qs)
    form.mobile_tag.data = mobile_tag

    log_info("mobile_tag_search", "end")
    return {'form':form}

@view_config(route_name='mobile_tag_search', context=ValidationFailure
    , request_type="altairsite.mobile.tweens.IMobileRequest"
    , renderer='altairsite.mobile:templates/common/error.mako')
def failed_validation(request):
    return {}
