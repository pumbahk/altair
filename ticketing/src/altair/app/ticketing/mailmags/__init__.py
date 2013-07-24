# encoding: utf-8

def includeme(config):
    config.add_route('mailmags.index', '/')
    config.add_route('mailmags.show', '/{id}')
    config.add_route('mailmags.edit', '/{id}/edit')
    config.add_route('mailmags.subscriptions.edit', '/{id}/subscriptions/edit')
    config.scan(".")
