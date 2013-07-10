from ticketing.models import (
    Base,
    DBSession,
)

from ticketing.core.models import (
    Event,
    Performance,
    ShippingAddress,
)

from ticketing.lots.models import (
    Lot,
    LotEntry,
)

class LotEntrySearch(Base):
    __table__ = LotEntry.__table__.join(
        Lot.__table__,
        Lot.id==LotEntry.lot_id
        ).join(
        Event.__table__,
        Event.id==Lot.event_id
        ).join(
        ShippingAddress.__table__,
        ShippingAddress.id==LotEntry.shipping_address_id)

    __mapper_args__ = dict(
        include_properties=[
            LotEntry.__table__.c.id,
            LotEntry.__table__.c.entry_no,
            Lot.__table__.c.id.label('lot_id'),
            Lot.__table__.c.name.label('lot_name'),
            Event.__table__.c.organization_id,
            Event.__table__.c.title,
            Event.__table__.c.id.label('event_id'),
            ShippingAddress.__table__.c.id.label('shipping_address_id'),
            ShippingAddress.__table__.c.last_name.label('shipping_address_last_name'),
            ShippingAddress.__table__.c.first_name.label('shipping_address_first_name'),
            ShippingAddress.__table__.c.last_name_kana.label('shipping_address_last_name_kana'),
            ShippingAddress.__table__.c.first_name_kana.label('shipping_address_first_name_kana'),
            ShippingAddress.__table__.c.prefecture.label('shipping_address_prefecture'),
            ShippingAddress.__table__.c.city.label('shipping_address_city'),
            ShippingAddress.__table__.c.address_1.label('shipping_address_address_1'),
            ShippingAddress.__table__.c.address_2.label('shipping_address_address_2'),
            ShippingAddress.__table__.c.tel_1.label('shipping_address_tel_1'),
            ShippingAddress.__table__.c.tel_2.label('shipping_address_tel_2'),
            ShippingAddress.__table__.c.email_1.label('shipping_address_email_1'),
            ShippingAddress.__table__.c.email_2.label('shipping_address_email_2'),
            LotEntry.__table__.c.created_at,
            ],
        primary_key=[
            LotEntry.__table__.c.id,
            ]
        )

    id = LotEntry.__table__.c.id
    entry_no = LotEntry.__table__.c.entry_no
    lot_id = Lot.__table__.c.id
    lot_name = Lot.__table__.c.name
    organization_id = Event.__table__.c.organization_id
    event_id = Event.__table__.c.id
    event_title = Event.__table__.c.title
    shipping_address_id = ShippingAddress.__table__.c.id
    shipping_address_last_name = ShippingAddress.__table__.c.last_name
    shipping_address_first_name = ShippingAddress.__table__.c.first_name
    shipping_address_last_name_kana = ShippingAddress.__table__.c.last_name_kana
    shipping_address_first_name_kana = ShippingAddress.__table__.c.first_name_kana
    shipping_address_prefecture = ShippingAddress.__table__.c.prefecture
    shipping_address_city = ShippingAddress.__table__.c.city
    shipping_address_address_1 = ShippingAddress.__table__.c.address_1
    shipping_address_address_2 = ShippingAddress.__table__.c.address_2
    shipping_address_tel_1 = ShippingAddress.__table__.c.tel_1
    shipping_address_tel_2 = ShippingAddress.__table__.c.tel_2
    shipping_address_email_1 = ShippingAddress.__table__.c.email_1
    shipping_address_email_2 = ShippingAddress.__table__.c.email_2
    created_at = LotEntry.__table__.c.created_at

    def __repr__(self):
        return ("<{0.__class__.__name__} "
                "organization_id={0.organization_id} "
                "entry_no={0.entry_no}>".format(self))
