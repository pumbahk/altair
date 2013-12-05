# -*- coding: utf-8 -*-
from altair.app.ticketing import newRootFactory
from .resources import DownloadResource

def includeme(config):
    config.add_route('cooperation.index', '/')
    config.add_route('cooperation.show', '/show/{venue_id}')
    config.add_route('cooperation.upload', '/upload/{venue_id}')

    download_factory = newRootFactory(DownloadResource)
    config.add_route('cooperation.download', '/download/{venue_id}', factory=download_factory)
    config.scan('.')
