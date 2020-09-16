# -*- coding:utf-8 -*-
from altair.app.ticketing.api.impl import bind_communication_api


def includeme(config):
    config.add_renderer('word_csv', '.renderers.WordCSVRenderer')
    config.add_route('word.index', '/', factory='.resources.WordResource')
    config.add_route('word.sync', '/sync/', factory='.resources.WordResource')
    config.add_route('word.download', '/download/{word_id}', factory='.resources.WordResource')
    bind_communication_api(config,
                           ".api.CMSWordsApi",
                           config.registry.settings["altair.cms.api_url"],
                           config.registry.settings["altair.cms.api_key"]
                           )
    config.scan(".")
