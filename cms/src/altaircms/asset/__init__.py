def includeme(config):
    config.add_route('asset_list', '/asset/')
    config.add_route('asset_form', '/asset/form/{asset_type}')
    config.add_route('asset_edit', '/asset/{asset_id}')
    config.add_route('asset_display', '/asset/display/{asset_id}')
    config.add_route('asset_view', '/asset/{asset_id}')

def get_storepath(request):
    return request.registry.settings['asset.storepath']

