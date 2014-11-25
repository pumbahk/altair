# encoding: utf-8
def smartphone_enabled(request):
    try:
        return request.organization.setting.enable_smartphone_cart
    except:
        # organization が host から取れないということもある
        return False
