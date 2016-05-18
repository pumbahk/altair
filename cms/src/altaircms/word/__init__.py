# coding: utf-8

def includeme(config):
    config.add_route('word_list', '/word/')
    config.add_crud("word", title="word", model="..models.Word",
                    form=".forms.WordForm",
                    bind_actions=["create", "delete", "update"],
                    has_auto_generated_permission=False, # FIXME:
                    mapper=".mappers.word_mapper",
                    events=dict(create_event=config.maybe_dotted(".subscribers.WordCreate"))
                    )
    config.add_route('event_list_for_word', '/word/event')
    config.add_route('word_create_back', '/word/created')

    ## subscriber
    config.add_subscriber(".views.after_created", ".subscribers.WordCreate")

    config.scan('.views')
