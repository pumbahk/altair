# -*- coding:utf-8 -*-
from ..lib.fanstatic_decorator import with_bootstrap
from pyramid.view import notfound_view_config, view_config, forbidden_view_config, view_defaults
from .models import Artist, Provider
from .forms import ArtistEditForm
from datetime import datetime
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from altaircms.models import DBSession


@view_defaults(decorator=with_bootstrap)
class ArtistView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def insert_provider(self, artist, provider_type):
        if self.request.POST[provider_type]:
            provider = Provider()
            provider.provider_type = provider_type
            provider.service_id = self.request.POST[provider_type]
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
        artist.name = self.request.POST['name']
        artist.kana = self.request.POST['kana']
        artist.code = self.request.POST['code']
        artist.url = self.request.POST['url']
        artist.image = self.request.POST['image']
        artist.description = self.request.POST['description']
        artist.public = 1 if self.request.POST['public'] else 0
        artist.organization_id = self.request.organization.id
        now = datetime.now()
        artist.created_at = now
        artist.updated_at = now
        self.insert_provider(artist, "twitter")
        self.insert_provider(artist, "facebook")
        self.insert_provider(artist, "line")
        DBSession.add(artist)
        self.request.session.flash(u'アーティストを追加しました。{}'.format(self.request.POST['name']))
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
        artist.name = self.request.POST['name']
        artist.kana = self.request.POST['kana']
        artist.code = self.request.POST['code']
        artist.url = self.request.POST['url']
        artist.image = self.request.POST['image']
        artist.set_service_id("twitter", self.request.POST['twitter'])
        artist.set_service_id("facebook", self.request.POST['facebook'])
        artist.set_service_id("line", self.request.POST['line'])
        artist.description = self.request.POST['description']
        artist.public = 1 if self.request.POST['public'] else 0
        artist.organization_id = self.request.organization.id
        now = datetime.now()
        artist.updated_at = now
        self.request.session.flash(u'アーティストを更新しました。{}'.format(self.request.POST['name']))
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
