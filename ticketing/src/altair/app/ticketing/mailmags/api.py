import logging

from sqlalchemy.orm import aliased
from altair.app.ticketing.models import DBSession
from . import models as mailmag_models

logger = logging.getLogger(__name__)

def get_magazines_to_subscribe(organization, emails):
    MailSubscription_alias = aliased(mailmag_models.MailSubscription)
    return [
        (
            mail_magazine,
            subscription is not None and \
            subscription.status not in [
                mailmag_models.MailSubscriptionStatus.Unsubscribed.v,
                mailmag_models.MailSubscriptionStatus.Reserved.v
                ]
            )
        for mail_magazine, subscription in (
            DBSession.query(mailmag_models.MailMagazine, mailmag_models.MailSubscription) \
                .outerjoin(
                    mailmag_models.MailSubscription,
                    (mailmag_models.MailMagazine.id == mailmag_models.MailSubscription.segment_id) & \
                    (mailmag_models.MailSubscription.email.in_(emails))) \
                .filter(mailmag_models.MailMagazine.organization_id == organization.id) \
                .filter(
                    ~mailmag_models.MailMagazine.id.in_(
                        DBSession.query(MailSubscription_alias.segment_id) \
                            .filter(
                                MailSubscription_alias.email.in_(emails) & \
                                (MailSubscription_alias.status.in_([
                                    mailmag_models.MailSubscriptionStatus.Reserved.v])) \
                                ) \
                            .distinct()
                        )
                    )
            )
        ]

def multi_subscribe(user, emails, magazine_ids):
    logger.debug("magazines: %s" % magazine_ids)
    for magazine in mailmag_models.MailMagazine.query.filter(mailmag_models.MailMagazine.id.in_(magazine_ids)).all():
        for email in emails:
            if magazine.subscribe(user, email):
                logger.debug("User %s starts subscribing %s for <%s>" % (user, magazine.name, email))
            else:
                logger.debug("User %s is already subscribing %s for <%s>" % (user, magazine.name, email))


