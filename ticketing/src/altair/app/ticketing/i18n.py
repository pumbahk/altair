from pyramid.i18n import get_localizer, TranslationStringFactory
from pyramid.events import NewRequest
from pyramid.events import subscriber
from webob.acceptparse import Accept
from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound

def add_renderer_globals(event):
    request = event.get('request')
    try:
        event['_'] = request.translate
        event['__'] = request.translate
        event['localizer'] = request.localizer
    except:
        pass

tsf = TranslationStringFactory('messages')

LOCALES = ('en', 'ja', 'zh_CN', 'zh_TW', 'ko')

def add_localizer(event):
    request = event.request
    def auto_translate(*args, **kwargs):
        return request.localizer.translate(tsf(*args, **kwargs))
    request.translate = auto_translate

def custom_locale_negotiator(request):
    name = '_LOCALE_'
    locale_name = getattr(request, name, None)

    # Set value with parameter
    if locale_name is None:
        locale_name = request.params.get(name)
    # Set value with cookies
    if locale_name is None:
        locale_name = request.cookies.get(name)
    # Set value with browser default language
    #if locale_name is None:
    #    locale_name = request.accept_language.best_match(LOCALES, request.registry.settings.default_locale_name)
    # Set value with application default settting
    if not request.accept_language:
        locale_name = request.registry.settings.default_locale_name
    if locale_name is None and request.organization._setting.i18n:
        locale_name = request.organization._setting.default_locale
    if locale_name is None:
        locale_name = 'ja'

    return locale_name

def set_locale_cookie(request):
    if request.GET['language']:
        language = request.GET['language']
        response = Response()
        response.set_cookie('_LOCALE_',
                            value=language,
                            max_age=31536000)  # max_age = year
    return HTTPFound(location=request.environ['HTTP_REFERER'],
                     headers=response.headers)
