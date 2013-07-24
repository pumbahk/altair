# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('organizations.index', '/')
    config.add_route('organizations.new', '/new')
    config.add_route('organizations.show', '/show/{organization_id}')
    config.add_route('organizations.edit', '/edit/{organization_id}')
    config.add_route('organizations.delete', '/delete/{organization_id}')

    config.add_route('organizations.sej_tenant.new', '/{organization_id}/sej_tenant/new')
    config.add_route('organizations.sej_tenant.edit', '/{organization_id}/sej_tenant/edit')
    config.add_route('organizations.sej_tenant.delete', '/{organization_id}/sej_tenant/delete')

    # config.add_route("organizations.mails.index", "/organizations/{organization_id}/mailinfo")
    ## mail_type is MailTypeEnum
    config.add_route("organizations.mails.new", "/{organization_id}/mailinfo/{mailtype}")
    config.scan(".")
