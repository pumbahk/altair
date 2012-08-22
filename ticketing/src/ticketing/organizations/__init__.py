# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('organizations.index', '/')
    config.add_route('organizations.new', '/new')
    config.add_route('organizations.show', '/show/{organization_id}')
    config.add_route('organizations.edit', '/edit/{organization_id}')
    config.add_route('organizations.delete', '/delete/{organization_id}')


    config.add_route('organizations.sej_tenant_new', '/sej/{organization_id}/new')
    config.add_route('organizations.sej_tenant_edit', '/sej/{organization_id}/edit/{id}')
    config.add_route('organizations.sej_tenant_delete', '/sej/{organization_id}/delete/{id}')

    config.scan(".")
