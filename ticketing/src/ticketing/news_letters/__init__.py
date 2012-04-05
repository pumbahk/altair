# -*- coding: utf-8 -*-
from ticketing.resources import *

def includeme(config):
    config.add_route('news_letters.index'   , '/')
    config.add_route('news_letters.new'     , '/new')
    config.add_route('news_letters.show'    , '/show/{news_letter_id}')
    config.add_route('news_letters.edit'    , '/edit/{news_letter_id}')
    config.add_route('news_letters.delete'  , '/delete/{news_letter_id}')
    config.add_route('news_letters.download', '/download/{news_letter_id}')
