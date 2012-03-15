
def add_routes(config):
    config.add_route('operators.index'          , '/')
    config.add_route('operators.new'            , '/new')
    config.add_route('operators.show'           , '/show/{operator_id}')
    config.add_route('operators.edit'           , '/edit/{operator_id}')
    config.add_route('operators.edit_multiple'  , '/edit_multiple')