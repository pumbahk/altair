# -*- coding:utf-8 -*-
from ..lib.fanstatic_decorator import with_bootstrap
from pyramid.view import notfound_view_config, view_config, forbidden_view_config, view_defaults
from .models import Artist, Provider
from ..event.models import Event
from .forms import ArtistEditForm, ArtistLinkForm, NowSettingForm
from datetime import datetime
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest
from altaircms.models import DBSession
from webob.multidict import MultiDict
from altair.now import (
    get_now,
    set_now,
    has_session_key
)
from altaircms.api import get_cart_domain
from altair.preview.api import (
    set_after_invalidate_url,
    set_force_request_type
)

@view_defaults(decorator=with_bootstrap)
class ArtistView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def insert_provider(self, artist, form, provider_type):
        if form.data[provider_type]:
            provider = Provider()
            provider.provider_type = provider_type
            provider.service_id = form.data[provider_type]
            provider.artist = artist

    @view_config(route_name="artist_list", request_method="GET",
                 renderer="altaircms:templates/artist/list.html", permission="artist_read")
    def artist_list_get(self):
        artists = self.request.allowable(Artist).all()
        return {'artists': artists}

    @view_config(route_name="artist_add", request_method="GET",
                 renderer="altaircms:templates/artist/add.html", permission="artist_create")
    def artist_add_get(self):
        form = ArtistEditForm(self.request.GET)
        return {'form': form}

    @view_config(route_name="artist_add", request_method="POST",
                 renderer="altaircms:templates/artist/add.html", permission="artist_create")
    def artist_add_post(self):
        form = ArtistEditForm(self.request.POST)
        if not form.validate():
            return {'form': form}
        artist = Artist()
        artist.name = form.data['name']
        artist.kana = form.data['kana']
        artist.code = form.data['code']
        artist.url = form.data['url']
        artist.image = form.data['image']
        artist.description = form.data['description']
        artist.public = form.data['public']
        artist.organization_id = self.request.organization.id
        now = datetime.now()
        artist.created_at = now
        artist.updated_at = now
        self.insert_provider(artist, form, "twitter")
        self.insert_provider(artist, form, "facebook")
        self.insert_provider(artist, form, "line")
        self.insert_provider(artist, form, "instagram")
        DBSession.add(artist)
        self.request.session.flash(u'アーティストを追加しました。{}'.format(form.data['name']))
        return HTTPFound(self.request.route_path('artist_list'))

    @view_config(route_name="artist_edit", request_method="GET",
                 renderer="altaircms:templates/artist/edit.html", permission="artist_update")
    def artist_edit_get(self):
        artist = self.request.allowable(Artist).filter(Artist.id == self.request.matchdict['artist_id']).first()
        if not artist:
            raise HTTPNotFound
        form = ArtistEditForm()
        form.id.data = artist.id
        form.name.data = artist.name
        form.kana.data = artist.kana
        form.code.data = artist.code
        form.url.data = artist.url
        form.image.data = artist.image
        form.description.data = artist.description
        form.public.data = artist.public
        form.twitter.data = artist.get_service_id("twitter")
        form.facebook.data = artist.get_service_id("facebook")
        form.line.data = artist.get_service_id("line")
        form.instagram.data = artist.get_service_id("instagram")
        return {'artist': artist, 'form': form}

    @view_config(route_name="artist_edit", request_method="POST",
                 renderer="altaircms:templates/artist/edit.html", permission="artist_update")
    def artist_edit_post(self):
        artist = self.request.allowable(Artist).filter(Artist.id == self.request.matchdict['artist_id']).first()
        if not artist:
            raise HTTPNotFound
        form = ArtistEditForm(self.request.POST)
        if not form.validate():
            return {'artist': artist, 'form': form}
        artist.name = form.data['name']
        artist.kana = form.data['kana']
        artist.code = form.data['code']
        artist.url = form.data['url']
        artist.image = form.data['image']
        artist.set_service_id("twitter", self.request.POST['twitter'])
        artist.set_service_id("facebook", self.request.POST['facebook'])
        artist.set_service_id("line", self.request.POST['line'])
        artist.set_service_id("instagram", self.request.POST['instagram'])
        artist.description = self.request.POST['description']
        artist.public = form.data['public']
        artist.organization_id = self.request.organization.id
        now = datetime.now()
        artist.updated_at = now
        self.request.session.flash(u'アーティストを更新しました。{}'.format(form.data['name']))
        return HTTPFound(self.request.route_path('artist_list'))

    @view_config(route_name="artist_delete", request_method="GET",
                 renderer="altaircms:templates/artist/list.html", permission="artist_delete")
    def artist_delete_get(self):
        artist = self.request.allowable(Artist).filter(Artist.id == self.request.matchdict['artist_id']).first()
        if not artist:
            raise HTTPNotFound
        DBSession.delete(artist)
        artists = self.request.allowable(Artist).all()
        return {'artists': artists}

    @view_config(route_name="event_link_artist", request_method="GET",
                 renderer="altaircms:templates/artist/link.html", permission="artist_update")
    def event_link_artist_get(self):
        event = self.request.allowable(Event).filter(Event.id == self.request.matchdict['event_id']).first()
        if not event:
            raise HTTPNotFound
        artists = self.request.allowable(Artist).all()
        form = ArtistLinkForm(formdata=MultiDict(artists=artists))
        if event.artist_id:
            form.artist.data = event.artist_id
        return {'event': event, 'form': form}

    @view_config(route_name="event_link_artist", request_method="POST",
                 renderer="altaircms:templates/artist/link.html", permission="artist_update")
    def event_link_artist_post(self):
        event_id = self.request.matchdict['event_id']
        event = self.request.allowable(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPNotFound
        form = ArtistLinkForm(self.request.POST)
        event.artist_id = form.artist.data
        self.request.session.flash(u'アーティストを紐付けました。イベント：{}'.format(event.title))
        return HTTPFound(self.request.route_path('event', id=event_id))

    @view_config(route_name="whattime_nowsetting_form", request_method="GET",
                 renderer="altaircms:templates/artist/whattime.html", permission="artist_read")
    def whattime_form_artist(self):
        now = get_now(self.request)

        artist = self.request.allowable(Artist).filter(Artist.id == self.request.matchdict['artist_id']).first()
        cart_url = get_cart_domain(self.request) + "/" + artist.url
        form = NowSettingForm(now=now, redirect_to=self.request.GET.get("redirect_to", cart_url))
        return {'artist': artist, 'form': form}

    @view_config(route_name="whattime_nowsetting_set", request_method="POST",
             request_param="submit",
             renderer="altaircms:templates/artist/whattime.html", permission="artist_read")
    def now_set_view(self):
        form = NowSettingForm(self.request.POST)
        artist = self.request.allowable(Artist).filter(Artist.id == self.request.matchdict['artist_id']).first()
        if not form.validate():
            return HTTPFound(self.request.route_path("whattime_nowsetting_form", artist_id=artist.id))

        set_now(self.request, form.data["now"])
        self.request.session.flash(u"現在時刻が「{now}」に設定されました".format(now=form.data["now"]))
        return HTTPFound(self.request.route_path("whattime_nowsetting_form", artist_id=artist.id))

    @view_config(route_name="whattime_nowsetting_set", request_method="POST", request_param="goto",
                 renderer="altaircms:templates/artist/whattime.html", permission="artist_read")
    def now_goto_view(self):
        artist = self.request.allowable(Artist).filter(Artist.id == self.request.matchdict['artist_id']).first()
        set_after_invalidate_url(self.request, self.request.route_url("whattime_nowsetting_form",
                                                                      artist_id=artist.id))
        nowday = self.request.params.get("now.year") + "-" + self.request.params.get("now.month") + "-" + self.request.params.get("now.day")
        nowtimes = self.request.params.get("now.hour") + ":" + self.request.params.get("now.minute") + ":" + self.request.params.get("now.second")

        if not has_session_key(self.request):
            self.request.session.flash(u"現在時刻が設定されていません")
            raise HTTPFound(self.request.route_path("whattime_nowsetting_form", artist_id=artist.id))
        return HTTPFound(self.request.params.get("redirect_to") + "?nowtime=" + nowday + " " + nowtimes)

    @view_config(route_name="whattime_nowsetting_set", request_method="POST",
                 request_param="invalidate",
                 renderer="altaircms:templates/artist/whattime.html", permission="artist_read")
    def now_invalidate_view(self):
        set_now(self.request, None)
        artist = self.request.allowable(Artist).filter(Artist.id == self.request.matchdict['artist_id']).first()
        self.request.session.flash(u"現在時刻の設定が取り消されました")
        return HTTPFound(self.request.route_path("whattime_nowsetting_form", artist_id=artist.id))

    @view_config(route_name="whattime_nowsetting_goto", request_param="redirect_to", permission="artist_read", request_method="POST")
    def now_goto_redirect_view(self):
        if "request_type" in self.request.GET:
            try:
                set_force_request_type(self.request, self.request.GET["request_type"])
            except ValueError:
                raise HTTPBadRequest("invalid request type")
        artist = self.request.allowable(Artist).filter(Artist.id == self.request.matchdict['artist_id']).first()
        if not has_session_key(self.request):
            self.request.session.flash(u"現在時刻が設定されていません")
            raise HTTPFound(self.request.route_path("whattime_nowsetting_form", artist_id=artist.id))
        set_after_invalidate_url(self.request, self.request.route_url("whattime_nowsetting_form", artist_id=artist.id))
        url = self.request.GET.get("redirect_to")

        return HTTPFound(self.request.GET.get("redirect_to") + "/" + self.request.GET.get("now"))