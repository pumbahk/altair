# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('newsletters.index' ,'/')
    config.add_route('newsletters.new' ,'/new')
    config.add_route('newsletters.copy' ,'/copy/{id}')
    config.add_route('newsletters.show' ,'/show/{id}')
    config.add_route('newsletters.edit' ,'/edit/{id}')
    config.add_route('newsletters.delete' ,'/delete/{id}')
    config.add_route('newsletters.download' ,'/download/{id}')
    config.add_route('newsletters.test_mail' ,'/test_mail/{id}')
    config.add_route('newsletters.htmlmail', '/htmlmail/{id}')

