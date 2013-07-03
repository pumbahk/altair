import functools
from .interfaces import IMailUtility
from .interfaces import IPurchaseInfoMail
from .interfaces import ITraverserFactory
from zope.interface.verify import verifyClass
from api import MailUtility
from api import MailTraverserFromOrder
from api import MailTraverserFromLotsEntry

def includeme(config):
    config.add_directive("add_order_mail_utility", register_order_mailutility)
    config.add_directive("add_lot_entry_mail_utility", register_lot_entry_mailutility)
    config.add_directive("add_mail_utility", register_mailutility)

def _register_order_mailutility(config, util, name):
    assert util.get_mailtype_description
    assert util.create_or_update_mailinfo
    assert util.get_subject_info_default
    assert util.get_traverser
    traverser_factory = MailTraverserFromOrder(name, default="")
    config.registry.registerUtility(traverser_factory, ITraverserFactory, name=name)
    _register_mailutility(config,util, name)

def _register_lot_entry_mailutility(config, util, name):
    assert util.get_mailtype_description
    assert util.create_or_update_mailinfo
    assert util.get_subject_info_default
    assert util.get_traverser
    traverser_factory = MailTraverserFromLotsEntry(name, default="")
    config.registry.registerUtility(traverser_factory, ITraverserFactory, name=name)
    _register_mailutility(config,util, name)

def _register_mailutility(config, util, name):
    assert util.build_message
    assert util.send_mail
    assert util.preview_text
    config.registry.registerUtility(util, IMailUtility, name=name)
    
def register_order_mailutility(config, name, module, mail, *args, **kwargs):
    name = str(name)
    module = config.maybe_dotted(module)
    verifyClass(IPurchaseInfoMail, mail)
    util = MailUtility(module, name, functools.partial(mail, *args, **kwargs))
    _register_order_mailutility(config, util, name)

def register_lot_entry_mailutility(config, name, module, mail, *args, **kwargs):
    name = str(name)
    module = config.maybe_dotted(module)
    util = MailUtility(module, name, functools.partial(mail, *args, **kwargs))
    _register_lot_entry_mailutility(config, util, name)

def register_mailutility(config, name, module, mail, *args, **kwargs):
    name = str(name)
    module = config.maybe_dotted(module)
    util = MailUtility(module, name, functools.partial(mail, *args, **kwargs))
    _register_mailutility(config, util, name)
    
