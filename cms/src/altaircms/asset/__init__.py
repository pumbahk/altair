def includeme(config):
    config.add_route('asset_list', '/asset/', factory=".resources.AssetResource")
    config.add_route('asset_display', '/asset/display/{asset_id}', factory=".resources.AssetResource")
    config.add_route('asset_view', '/asset/{asset_id}', factory=".resources.AssetResource")
    config.add_route('asset_delete', '/asset/{asset_id}/delete', factory=".resources.AssetResource")
    config.add_route('asset_create', '/asset/{asset_type}/create', factory=".resources.AssetResource")
    # config.add_route('asset_form', '/asset/form/{asset_type}')
    # config.add_route('asset_edit', '/asset/{asset_id}')

EXT_MAP = {
    'jpg':'image/jpeg',
    'jpeg':'image/jpeg',
    'png':'image/png',
    'gif':'image/gif',
    'mov':'video/quicktime',
    'mp4':'video/quicktime',
    'swf':'application/x-shockwave-flash',
}

def detect_mimetype(filename):
    ext = filename[filename.rfind('.') + 1:].lower()
    return EXT_MAP[ext] if ext in EXT_MAP else 'application/octet-stream'

def get_storepath(request):
    return request.registry.settings['altaircms.asset.storepath']

