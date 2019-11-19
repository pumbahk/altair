from pyramid.i18n import get_localizer, TranslationStringFactory

tsf = TranslationStringFactory('coupon')

def add_localizer(event):
    request = event.request
    localizer = get_localizer(request)
    def auto_translate(*args, **kwargs):
        return localizer.translate(tsf(*args, **kwargs))
    request.localizer = localizer
    request.translate = auto_translate
