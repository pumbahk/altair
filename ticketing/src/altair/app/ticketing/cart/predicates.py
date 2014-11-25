def smartphone_enabled(request):
    return request.organization.setting.enable_smartphone_cart
