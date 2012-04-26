def includeme(config):
    config.add_route('products.index'          , '/')

    # Product JSON API
    config.add_route('products.json.list'       , '/json.list')
    config.add_route('products.json.new'        , '/json.new')
    config.add_route('products.json.show'       , '/json.show/{product_id}')
    config.add_route('products.json.update'     , '/json.update/{product_id}')
    #

    config.add_route('products.sales_segments'          , '/segments')
    config.add_route('products.sales_segments.new'      , '/segments/new')

    config.add_route('products.payment_delivery_method'         , '/payment_delivery_method')
    config.add_route('products.payment_delivery_method.list'     , '/payment_delivery_method/list')


