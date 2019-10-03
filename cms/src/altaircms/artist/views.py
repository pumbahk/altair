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
from .api import AESCipher, checkinput
import urllib
import logging
logger = logging.getLogger(__name__)

from altaircms.api import get_cart_domain
from altair.preview.api import (
    set_after_invalidate_url
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
        self.insert_provider(artist, form, "official")
        self.insert_provider(artist, form, "funclub")
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
        form.official.data = artist.get_service_id("official")
        form.funclub.data = artist.get_service_id("funclub")
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
        artist.set_service_id("official", self.request.POST['official'])
        artist.set_service_id("funclub", self.request.POST['funclub'])
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
        now = datetime.now();

        artist = self.request.allowable(Artist).filter(Artist.id == self.request.matchdict['artist_id']).first()
        cart_url = get_cart_domain(self.request) + "/" + artist.url
        form = NowSettingForm(now=now, redirect_to=self.request.GET.get("redirect_to", cart_url))
        return {'artist': artist, 'form': form}

    @view_config(route_name="whattime_nowsetting_goto", request_method="POST", request_param="goto",
                 renderer="altaircms:templates/artist/whattime.html", permission="artist_read")
    def now_goto_view(self):
        artist = self.request.allowable(Artist).filter(Artist.id == self.request.matchdict['artist_id']).first()
        set_after_invalidate_url(self.request, self.request.route_url("whattime_nowsetting_form",
                                                                      artist_id=artist.id))
        params = self.request.params

        nowday = "{0}-{1}-{2}".format(params.get("now.year"), params.get("now.month"), params.get("now.day"))
        nowtimes = "{0}:{1}:{2}".format(params.get("now.hour"), params.get("now.minute"), params.get("now.second"))
        nowtime = "{0} {1}".format(nowday, nowtimes)

        if checkinput(nowtime):
            aeskey = self.request.registry.settings.get("aes.artist.nowtime.secret.key")
            cipher = AESCipher(aeskey)
            encryptstr = cipher.encrypt(nowtime)
            urllibstr = urllib.quote(encryptstr)

            return HTTPFound(self.request.params.get("redirect_to") + "?t=" + urllibstr)
        else:
            return HTTPFound(self.request.params.get("redirect_to"))
