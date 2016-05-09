# coding: utf-8

def includeme(config):
    config.add_route('word_list', '/word/')
    config.add_crud("word", title="word", model="..models.Word",
                    form=".forms.WordForm",
                    bind_actions=["create", "delete", "update"],
                    has_auto_generated_permission=False, # FIXME:
                    mapper=".mappers.word_mapper",
                    events=dict(),
                    )
    config.add_route('event_list_for_word', '/word/event')
    config.scan('.views')
