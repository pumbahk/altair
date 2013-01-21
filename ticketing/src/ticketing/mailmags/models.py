from sqlalchemy import Table, Column, Boolean, BigInteger, Integer, Float, String, Date, DateTime, ForeignKey, DECIMAL, Index, UniqueConstraint
from sqlalchemy.orm import join, backref, column_property
from ticketing.models import Base, BaseModel, WithTimestamp, LogicallyDeleted, Identifier, relationship
import sqlahelper

from ticketing.utils import StandardEnum

session = sqlahelper.get_session()
Base = sqlahelper.get_base()

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

        # Do nothing if the user is subscribing the magazine
        # with the same e-mail address.
        if subscription:
            return None
        subscription = MailSubscription(email=mail_address, user=user, segment=self)
        session.add(subscription)
        return subscription

    def unsubscribe(self, user, mail_address):
        subscription = MailSubscription.query.filter(
            MailSubscription.user==user,
            MailSubscription.email==mail_address
        ).filter(
            MailSubscription.segment==mailmagazine
        ).first()
        if subscription:
            session.delete(subscription)

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


