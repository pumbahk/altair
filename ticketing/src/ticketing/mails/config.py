import functools
from .interfaces import IMailUtility
from api import MailUtility

def includeme(config):
    config.add_directive("add_order_mail_utility", register_order_mailutility)
    config.add_directive("add_mail_utility", register_mailutility)

def create_mail_utility_from_mail(mail, module, args, kwargs):
    return MailUtility(module, functools.partial(mail, *args, **kwargs))

def _register_order_mailutility(config, util, name):
    assert util.get_mailtype_description
    assert util.create_or_update_mailinfo
    assert util.get_order_info_default
    assert util.get_traverser
    _register_mailutility(config,util, name)

def _register_mailutility(config, util, name):
    name = str(name)
    assert util.build_message
    assert util.send_mail
    assert util.preview_text
    config.registry.registerUtility(util, IMailUtility, name=name)
    
def register_order_mailutility(config, name, module, mail, *args, **kwargs):
    module = config.maybe_dotted(module)
    util = create_mail_utility_from_mail(mail, module, args, kwargs)
    _register_order_mailutility(config, util, name)

def register_mailutility(config, name, module, mail, *args, **kwargs):
    module = config.maybe_dotted(module)
    util = create_mail_utility_from_mail(mail, module, args, kwargs)
    _register_mailutility(config, util, name)
    
