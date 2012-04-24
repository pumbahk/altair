def includeme(config):
    config.add_route('products.index'          , '/')
    config.add_route('products.sales_segments'          , '/segments')
    config.add_route('products.sales_segments.new'      , '/segments/new')

    config.add_route('products.payment_delivery_method'         , '/payment_delivery_method')
    config.add_route('products.payment_delivery_method.list'     , '/payment_delivery_method/list')


