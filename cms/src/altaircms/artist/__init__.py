# -*- coding:utf-8 -*-


def includeme(config):
    config.add_route("artist_list", "/artist/", factory='.resources.ArtistResource')
    config.scan(".views")
