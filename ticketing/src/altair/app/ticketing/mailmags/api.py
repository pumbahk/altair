import logging

from altair.app.ticketing.models import DBSession
from . import models as mailmag_models

logger = logging.getLogger(__name__)

def get_magazines_to_subscribe(organization, emails):
    return organization.mail_magazines \
        .filter(
            ~mailmag_models.MailMagazine.id.in_(
                DBSession.query(mailmag_models.MailMagazine.id) \
                    .join(mailmag_models.MailSubscription.segment) \
                    .filter(
                        mailmag_models.MailSubscription.email.in_(emails) & \
                        (mailmag_models.MailSubscription.status.in_([
                            mailmag_models.MailSubscriptionStatus.Subscribed.v,
                            mailmag_models.MailSubscriptionStatus.Reserved.v]) | \
                         (mailmag_models.MailSubscription.status == None)) \
                        ) \
                    .distinct()
                )
            ) \
        .all()

def multi_subscribe(user, emails, magazine_ids):
    logger.debug("magazines: %s" % magazine_ids)
    for magazine in mailmag_models.MailMagazine.query.filter(mailmag_models.MailMagazine.id.in_(magazine_ids)).all():
        for email in emails:
            if magazine.subscribe(user, email):
                logger.debug("User %s starts subscribing %s for <%s>" % (user, magazine.name, email))
            else:
                logger.debug("User %s is already subscribing %s for <%s>" % (user, magazine.name, email))


