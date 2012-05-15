def includeme(config):
    config.add_route('products.delete', '/delete/{product_id}')
    config.add_route('products.delete_item', '/delete_item/{product_item_id}')

    # Product JSON API
    config.add_route('products.json.list', '/json.list')
    config.add_route('products.json.new', '/json.new')
    config.add_route('products.json.show', '/json.show/{product_id}')
    config.add_route('products.json.update', '/json.update/{product_id}')

    config.add_route('products.json.new_item', '/json.new_item')
    config.add_route('products.json.edit_item', '/json.edit_item/{product_item_id}')
