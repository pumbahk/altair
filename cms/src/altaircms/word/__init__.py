# coding: utf-8

def includeme(config):
    config.add_route('word', '/word/')
    config.add_crud("word", title="word", model="..models.Word",
                    form=".forms.WordForm",
                    bind_actions=["create", "delete", "update"],
                    has_auto_generated_permission=False, # FIXME:
                    mapper=".mappers.word_mapper",
                    events=dict(),
                    )
    config.scan('.views')
