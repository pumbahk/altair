
def includeme(config):
    config.add_route('operators.index'          , '/')
    config.add_route('operators.new'            , '/new')
    config.add_route('operators.show'           , '/show/{operator_id}')
    config.add_route('operators.edit'           , '/edit/{operator_id}')
    config.add_route('operators.edit_multiple'  , '/edit_multiple')

    config.add_route('operator_roles.index'          , '/roles')
    config.add_route('operator_roles.new'            , '/roles/new')
    config.add_route('operator_roles.show'           , '/roles/show/{operator_role_id}')
    config.add_route('operator_roles.edit'           , '/roles/edit/{operator_role_id}')
    config.add_route('operator_roles.edit_multiple'  , '/roles/edit_multiple')

    config.add_route('permissions.index'             , '/permissions')

    config.add_route('operators.organization.index'  , '/organization/')
    config.add_route('operators.organization.new'    , '/organization/new')
    config.add_route('operators.organization.show'   , '/organization/show/{operator_id}')
    config.add_route('operators.organization.edit'   , '/organization/edit/{operator_id}')
