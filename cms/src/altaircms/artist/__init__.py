# -*- coding:utf-8 -*-


def includeme(config):
    config.add_route("artist_list", "/artist/", factory='.resources.ArtistResource')
    config.add_route("artist_add", "/artist/add", factory='.resources.ArtistResource')
    config.add_route("artist_edit", "/artist/edit", factory='.resources.ArtistResource')
    config.add_route("artist_delete", "/artist/delete", factory='.resources.ArtistResource')
    config.scan(".views")
