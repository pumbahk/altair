from pyramid_mailer.interfaces import IMailer
import logging
from zope.interface import implementer

logger = logging.getLogger(__name__)

@implementer(IMailer)
class DevNullMailer(object):
    """
    this is like a pyramid_mailer.mailer.DummyMailer.
    but, this class *does not* store sent mail.
    """
    def send(self, message):    
        logger.info("*mail* send %s" % message)

    def send_immediately(self, message, fail_silently=False):
        logger.info("*mail* send_immediately(fail_silently=%s) %s" % (fail_silently, message))


    def send_to_queue(self, message):
        logger.info("*mail* send to queue %s" % message)

def devnull_mailer(config):
    mailer = DevNullMailer()
    config.registry.registerUtility(mailer, IMailer)
