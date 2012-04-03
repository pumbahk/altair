def includeme(config):

    config.add_route('performances.index'            , '/')
    config.add_route('performances.new'              , '/new')
    config.add_route('performances.show'             , '/show/{performance_id}')
    config.add_route('performances.edit'             , '/edit/{performance_id}')
    config.add_route('performances.edit_multiple'    , '/edit_multiple')
    config.add_route('performances.delete'           , '/delete/{performance_id}')
