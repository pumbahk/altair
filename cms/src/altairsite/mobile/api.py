from altair.cdnpath import PrefixedStaticURLInfo

def mobile_static_url(request):
    def create_mobile_static_url(path):
        prefix = request.host
        return PrefixedStaticURLInfo(prefix, None, None)._generate(path=path, request=request)
    return create_mobile_static_url
