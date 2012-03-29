def includeme(config):

    config.add_route('performances.index'            , '/')
    config.add_route('performances.new'              , '/new')
    config.add_route('performances.show'             , '/show/{event_id}')
    config.add_route('performances.edit'             , '/edit/{event_id}')
    config.add_route('performances.edit_multiple'    , '/edit_multiple')
    config.add_route('performances.delete'           , '/delete/{event_id}')
