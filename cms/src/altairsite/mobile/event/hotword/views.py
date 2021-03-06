# -*- coding: utf-8 -*-
from altaircms.datelib import get_now
from altaircms.tag.models import HotWord
from altaircms.page.models import PageSet, PageTag2Page, PageTag
from altaircms.event.models import Event
from altaircms.models import Genre
from altairsite.config import mobile_site_view_config
from altairsite.mobile.event.hotword.forms import HotwordForm
from altairsite.mobile.core.helper import exist_value
from altairsite.mobile.core.helper import get_week_map, get_event_paging
from altairsite.mobile.core.helper import log_info
from altairsite.exceptions import UsersiteException
from altairsite.separation import selectable_renderer

class ValidationFailure(UsersiteException):
    pass

@mobile_site_view_config(route_name='hotword', request_type="altair.mobile.interfaces.IMobileRequest"
    , renderer=selectable_renderer('altairsite.mobile:templates/%(prefix)s/searchresult/hotword_result.mako'))
def move_hotword(request):

    log_info("move_hotword", "start")
    form = HotwordForm(request.GET)
    form.week.data = get_week_map()

    if not exist_value(form.id.data):
        log_info("move_hotword", "hotword id not found")
        raise ValidationFailure

    today = get_now(request)
    hotword = request.allowable(HotWord).filter(HotWord.term_begin <= today) \
        .filter(today <= HotWord.term_end) \
        .filter_by(enablep=True).filter(HotWord.id == form.id.data).first()

    if not hotword:
        log_info("move_hotword", "hotword not found")
        raise ValidationFailure

    qs = request.allowable(Event) \
                .filter(Event.is_searchable == True) \
                .join(PageSet, Event.id == PageSet.event_id) \
                .join(PageTag2Page, PageSet.id == PageTag2Page.object_id) \
                .join(PageTag, PageTag2Page.tag_id == PageTag.id) \
                .filter(PageTag.id == hotword.tag_id)

    form = get_event_paging(request=request, form=form, qs=qs)

    # パンくずリスト用
    log_info("move_hotword", "breadcrumb create start")
    form.navi_hotword.data = hotword
    if exist_value(form.genre.data):
        form.navi_genre.data = request.allowable(Genre).filter(Genre.id==form.genre.data).first()

    if exist_value(form.sub_genre.data):
        form.navi_sub_genre.data = request.allowable(Genre).filter(Genre.id==form.sub_genre.data).first()
    log_info("move_hotword", "breadcrumb create end")

    log_info("move_hotword", "end")
    return {'form':form}

@mobile_site_view_config(route_name='hotword', context=ValidationFailure
    , request_type="altair.mobile.interfaces.IMobileRequest", renderer=selectable_renderer('altairsite.mobile:templates/%(prefix)s/common/error.mako'))
def failed_validation(request):
    return {}
