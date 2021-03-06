import functools
import re
from .interfaces import IMailUtility
from .interfaces import IPurchaseInfoMail
from .interfaces import ITraverserFactory
from .interfaces import IMessagePartFactory
from zope.interface.verify import verifyClass, verifyObject
from api import MailUtility
from api import MailTraverserFromOrder
from api import MailTraverserFromLotsEntry
from api import MailTraverserFromPointGrantHistoryEntry
from api import MessagePartFactory

def includeme(config):
    config.add_directive("add_order_mail_utility", register_order_mailutility)
    config.add_directive("add_lot_entry_mail_utility", register_lot_entry_mailutility)
    config.add_directive("add_point_grant_history_entry_mail_utility", register_point_grant_history_entry_mailutility)
    config.add_directive("add_mail_utility", register_mailutility)
    config.add_directive("add_message_part_factory", register_message_part_factory)

def _register_order_mailutility(config, util, name):
    traverser_factory = MailTraverserFromOrder(name, default="")
    config.registry.registerUtility(traverser_factory, ITraverserFactory, name=name)
    _register_mailutility(config,util, name)

def _register_lot_entry_mailutility(config, util, name):
    traverser_factory = MailTraverserFromLotsEntry(name, default="")
    config.registry.registerUtility(traverser_factory, ITraverserFactory, name=name)
    _register_mailutility(config,util, name)

def _register_point_grant_history_entry_mailutility(config, util, name):
    traverser_factory = MailTraverserFromPointGrantHistoryEntry(name, default="")
    config.registry.registerUtility(traverser_factory, ITraverserFactory, name=name)
    _register_mailutility(config, util, name)

def _register_mailutility(config, util, name):
    verifyObject(IMailUtility, util)
    config.registry.registerUtility(util, IMailUtility, name=name)

def _register_message_part_factory(config, factory, name):
    config.registry.registerUtility(factory, IMessagePartFactory, name=name)

def register_order_mailutility(config, name, module, mail, *args, **kwargs):
    name = str(name)
    module = config.maybe_dotted(module)
    verifyClass(IPurchaseInfoMail, mail)
    util = MailUtility(module, name, mail(*args, **kwargs))
    _register_order_mailutility(config, util, name)

def register_lot_entry_mailutility(config, name, module, mail, *args, **kwargs):
    name = str(name)
    module = config.maybe_dotted(module)
    util = MailUtility(module, name, mail(*args, **kwargs))
    _register_lot_entry_mailutility(config, util, name)

def register_point_grant_history_entry_mailutility(config, name, module, mail, *args, **kwargs):
    name = str(name)
    module = config.maybe_dotted(module)
    util = MailUtility(module, name, mail(*args, **kwargs))
    _register_point_grant_history_entry_mailutility(config, util, name)

def register_mailutility(config, name, module, mail, *args, **kwargs):
    def register():
        name = str(name)
        module = config.maybe_dotted(module)
        util = MailUtility(module, name, mail(*args, **kwargs))
        _register_mailutility(config, util, name)
    config.action('%s:%s' % (__name__, name), register)

def register_message_part_factory(config, name, content_type):
    charset = config.registry.settings.get('altair.mails.mpf.%s.charset' % name, None)
    encoding = config.registry.settings.get('altair.mails.mpf.%s.encoding' % name, None)
    _filters = config.registry.settings.get('altair.mails.mpf.%s.filters' % name, '').strip()
    filters = map(config.maybe_dotted, re.split(r'\s*,\s*', _filters) if _filters else [])
    encode_errors = config.registry.settings.get('altair.mails.mpf.%s.encode_errors' % name, 'strict')
    transfer_encoding = config.registry.settings.get('altair.mails.mpf.%s.transfer_encoding' % name, None)
    factory = MessagePartFactory(content_type, charset, encoding, encode_errors, filters, transfer_encoding)
    _register_message_part_factory(config, factory, name) 
