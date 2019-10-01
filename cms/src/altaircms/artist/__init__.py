# -*- coding:utf-8 -*-


def includeme(config):
    config.add_route("artist_list", "/artist/", factory='.resources.ArtistResource')
    config.add_route("artist_add", "/artist/add", factory='.resources.ArtistResource')
    config.add_route("artist_edit", "/artist/edit/{artist_id}", factory='.resources.ArtistResource')
    config.add_route("artist_delete", "/artist/delete/{artist_id}", factory='.resources.ArtistResource')
    config.add_route("event_link_artist", "/event/link/artist/{event_id}", factory='.resources.ArtistResource')
    config.add_route("whattime_nowsetting_form", "/artist/whattime_form/{artist_id}", factory='.resources.ArtistResource')
    config.add_route("whattime_nowsetting_goto", "/whattime/goto/{artist_id}", factory=".resources.ArtistResource")
    config.scan(".views")
