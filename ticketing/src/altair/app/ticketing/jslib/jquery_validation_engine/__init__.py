from fanstatic import Library, Resource
from js.jquery import jquery

library = Library('jquery_validation_engine', 'resources')

validation_engine_main_js = Resource(
    library, 
    'jquery.validationEngine.js',
    depends=[jquery]
)

validation_engine_main_css = Resource(
    library,
    'validationEngine.jquery.css'
)

validation_engine = {}

for lang in ("cz", "da", "de", "en", "es", "fr",
             "it", "ja", "nl", "pl", "pt", "ro",
             "ru", "tr"):

    validation_engine[lang] = Resource(
        library, 
        'jquery.validationEngine-%s.js' % lang,
        depends=[validation_engine_main_js, validation_engine_main_css]
    )