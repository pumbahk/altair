def includeme(config):
    config.add_route('products.index', '/')

    # Product JSON API
    config.add_route('products.json.list', '/json.list')
    config.add_route('products.json.new', '/json.new')
    config.add_route('products.json.show', '/json.show/{product_id}')
    config.add_route('products.json.update', '/json.update/{product_id}')
    #

    config.add_route('products.sales_segments', '/segments')
    config.add_route('products.sales_segments.show', '/segments/show/{sales_segment_id}')

    config.add_route('products.payment_delivery_method_pair.new', '/payment_delivery_method/{sales_segment_id}/new')
    config.add_route('products.payment_delivery_method_pair.list', '/payment_delivery_method/list')
