# encoding: utf-8
from pyramid.i18n import TranslationStringFactory
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.attributes import instance_state
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm.session import make_transient
from altair.sqlahelper import get_db_session
from altair.app.ticketing.extauth  import models
from altair.app.ticketing.security import get_extra_auth_info_from_principals
from pyramid.security import Everyone

ENV_ORGANIZATION_ID_KEY = 'altair.app.ticketing.extauth.organization_id'
ENV_ORGANIZATION_PATH_KEY = 'altair.app.ticketing.extauth.organization_path'

def get_organization(request):
    session = get_db_session(request, 'extauth_slave')
    try:
        organization = session.query(models.Organization) \
            .join(models.Host, models.Organization.id == models.Host.organization_id) \
            .filter(models.Host.host_name == unicode(request.host)) \
            .one()
    except (NoResultFound, MultipleResultsFound) as e:
        raise Exception("Host that named %s is not Found" % request.host)
    make_transient(organization)
    return organization


def add_extauth_localizer(event):
    request = event.request
    factory = TranslationStringFactory('extauth')

    def auto_translate(*args, **kwargs):
        return request.localizer.translate(factory(*args, **kwargs))
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
    if not request.accept_language:
        locale_name = request.registry.settings.default_locale_name
    if locale_name is None:
        locale_name = 'ja'

    return locale_name


def includeme(config):
    from datetime import datetime
    config.add_request_method(get_organization, 'organization', reify=True)
    config.add_request_method(lambda request: datetime.now(), 'now', reify=True)
    # i18n setting
    config.add_subscriber('altair.app.ticketing.i18n.add_renderer_globals', 'pyramid.events.BeforeRender')
    config.add_subscriber(add_extauth_localizer, 'pyramid.events.NewRequest')
    config.add_translation_dirs('altair.app.ticketing:locale')
    config.set_locale_negotiator(custom_locale_negotiator)
