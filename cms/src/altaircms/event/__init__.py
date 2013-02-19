# coding: utf-8
from .interfaces import IAPIKeyValidator, IEventRepository

def includeme(config):
    config.add_route('event', '/event/{id}')
    config.add_route('event_detail', '/event/{id}/{section}')
    config.add_route("event_takein_pageset", "/event/{event_id}/takein/pageset")
    config.add_route('event_list', '/event/')
    config.add_crud("event", title="event", model=".models.Event",
                    form=".forms.EventForm", mapper=".mappers.event_mapper", 
                    bind_actions=["create", "delete", "update"], 
                    events=dict(create_event=config.maybe_dotted(".subscribers.EventCreate"), 
                                update_event=config.maybe_dotted(".subscribers.EventUpdate"), 
                                delete_event=config.maybe_dotted(".subscribers.EventDelete"), 
                                ))

    ## bind event
    config.add_subscriber(".subscribers.event_register_solr", ".subscribers.EventCreate")
    config.add_subscriber(".subscribers.event_register_solr", ".subscribers.EventUpdate")
    config.add_subscriber(".subscribers.event_delete_solr", ".subscribers.EventDelete") ## fixme

    config.add_subscriber(".subscribers.flash_view_page_url", ".subscribers.EventCreate")
    config.add_subscriber(".subscribers.flash_view_page_url", ".subscribers.EventUpdate")


    # バックエンドからの受取り用。
    # 認証方式が異なるため独立したインターフェースを設ける。
    config.add_route('api_event_register', '/api/event/register')

    reg = config.registry
    validate_apikey = config.maybe_dotted('.api.validate_apikey')
    reg.registerUtility(validate_apikey, IAPIKeyValidator)
    event_repository = config.maybe_dotted('.api.EventRepositry')
    reg.registerUtility(event_repository(), IEventRepository)

    # バックエンドへの受け渡し用(受け取り用と同じAPIトークンを使う。)
    config.add_route("api_event_info", "/api/event/{event_id}/info")
    config.scan(".views")
