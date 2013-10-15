def encoding_converter_tween_factory(handler, registry):
    def encoding_converter_tween(request):
        registry = getattr(request, 'registry', None)
        context = getattr(request, 'context', None)
        request = request.decode('CP932')
        if registry is not None:
            request.registry = registry
        if context is not None:
            request.context = context
        return handler(request)
    return encoding_converter_tween
