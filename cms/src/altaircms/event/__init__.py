# coding: utf-8
from .interfaces import IAPIKEYValidator, IEventRepositiry

def includeme(config):
    config.add_route('event', '/event/{id}')
    config.add_route('event_list', '/event/')
    config.add_crud("event", title="event", model=".models.Event",
                    form=".forms.EventForm", mapper=".mappers.event_mapper", 
                    bind_actions=["create", "delete", "update"])

    # バックエンドからの受取り用。
    # 認証方式が異なるため独立したインターフェースを設ける。
    config.add_route('api_event_register', '/api/event/register')

    reg = config.registry
    validate_apikey = config.maybe_dotted('.api.validate_apikey')
    reg.registerUtility(validate_apikey, IAPIKEYValidator)
    event_repository = config.maybe_dotted('.api.EventRepositry')
    reg.registerUtility(event_repository, IEventRepositiry)

    config.scan()
