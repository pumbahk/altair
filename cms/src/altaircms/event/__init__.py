# coding: utf-8
from .interfaces import IAPIKeyValidator, IEventRepository

def includeme(config):
    config.add_route('event', '/event/{id}')
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

    # バックエンドからの受取り用。
    # 認証方式が異なるため独立したインターフェースを設ける。
    config.add_route('api_event_register', '/api/event/register')

    reg = config.registry
    validate_apikey = config.maybe_dotted('.api.validate_apikey')
    reg.registerUtility(validate_apikey, IAPIKeyValidator)
    event_repository = config.maybe_dotted('.api.EventRepositry')
    reg.registerUtility(event_repository(), IEventRepository)

    config.scan()
