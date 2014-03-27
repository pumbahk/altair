# -*- coding: utf-8 -*-

from altair.app.ticketing import newRootFactory

def includeme(config):
    from altair.app.ticketing.operators.resources import OperatorAdminResource
    factory = newRootFactory(OperatorAdminResource)

    config.add_route('operators.index', '/', factory=factory)
    config.add_route('operators.new', '/new', factory=factory)
    config.add_route('operators.show', '/show/{operator_id}', factory=factory)
    config.add_route('operators.edit', '/edit/{operator_id}', factory=factory)
    config.add_route('operators.delete', '/delete/{operator_id}', factory=factory)

    config.add_route('operator_roles.index', '/roles', factory=factory)
    config.add_route('operator_roles.new', '/roles/new', factory=factory)
    config.add_route('operator_roles.edit', '/roles/edit/{operator_role_id}', factory=factory)
    config.add_route('operator_roles.delete', '/roles/delete/{operator_role_id}', factory=factory)

    config.add_route('permissions.index', '/permissions', factory=factory)

    config.scan(".")
