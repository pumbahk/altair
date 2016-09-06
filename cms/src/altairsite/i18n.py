from pyramid.i18n import get_localizer, TranslationStringFactory

tsf = TranslationStringFactory('search')

def add_localizer(event):
    request = event.request
    def auto_translate(*args, **kwargs):
        return request.localizer.translate(tsf(*args, **kwargs))
    request.translate = auto_translate
