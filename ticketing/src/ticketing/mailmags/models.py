from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, DECIMAL, Index, UniqueConstraint
from sqlalchemy.orm import join, backref, column_property
from ticketing.models import Base, BaseModel, WithTimestamp, LogicallyDeleted, Identifier, relationship
import sqlahelper
import logging

from ticketing.utils import StandardEnum

session = sqlahelper.get_session()
Base = sqlahelper.get_base()

logger = logging.getLogger(__name__)

class MailMagazine(Base, BaseModel, WithTimestamp):
    __tablename__ = 'MailMagazine'
    query = session.query_property()
    id = Column(Identifier, primary_key=True)
    name = Column(String(255))
    description = Column(String(1024))
    organization_id = Column(Identifier, ForeignKey("Organization.id"), nullable=True)
    organization = relationship('Organization', uselist=False, backref='mail_magazines')
    status = Column(Integer)

    def subscribe(self, user, mail_address):
        subscription = MailSubscription.query.filter(
            #MailSubscription.user==user,
            MailSubscription.email==mail_address
        ).filter(
            MailSubscription.segment==self
        ).first()

        if subscription:
            if subscription.status == MailSubscriptionStatus.Unsubscribed.v:
                subscription.status = MailSubscriptionStatus.Subscribed.v
            else:
                logger.warning("trying to let {0} subscribe MailMagazine (id={1.id}, name={1.name}) which is {2}".format(mail_address, self, "already subscribed" if subscription.status is None or subscription.status == MailSubscriptionStatus.Subscribed else "reserved"))
        else:
            subscription = MailSubscription(email=mail_address, user=user, segment=self, status=MailSubscriptionStatus.Subscribed.v)
            session.add(subscription)
        return subscription

    def unsubscribe(self, user, mail_address):
        subscription = MailSubscription.query.filter(
            MailSubscription.user==user,
            MailSubscription.email==mail_address
        ).filter(
            MailSubscription.segment==self
        ).first()
        if subscription is not None:
            subscription.unsubscribe()

class MailSubscriptionStatus(StandardEnum):
    Unsubscribed = 0
    Subscribed = 1
    Reserved = 2

class MailSubscription(Base, BaseModel, LogicallyDeleted, WithTimestamp):
    __tablename__ = 'MailSubscription'
    __table_args__ = (
        Index('email_segment_idx', 'email', 'segment_id', unique=True),
        )
    query = session.query_property()
    id = Column(Identifier, primary_key=True)
    email = Column(String(255))
    user_id = Column(Identifier, ForeignKey("User.id"), nullable=True)
    user = relationship('User', uselist=False, backref='mail_subscription')
    segment_id = Column(Identifier, ForeignKey("MailMagazine.id"), nullable=True)
    segment = relationship('MailMagazine', uselist=False, backref='subscriptions')

    status = Column(Integer)

    def unsubscribe(self):
        self.status = MailSubscriptionStatus.Unsubscribed.v
