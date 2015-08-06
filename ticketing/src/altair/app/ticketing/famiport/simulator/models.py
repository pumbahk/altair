import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData

metadata = MetaData()
Base = declarative_base(metadata=metadata)

class FDCSideTicket(Base):
    __tablename__ = 'FDCSideTicket'

    id                           = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    fdc_side_order_id            = sa.Column(sa.Integer, sa.ForeignKey('FDCSideOrder.id'), nullable=False)
    type                         = sa.Column(sa.Integer, nullable=True)
    barcode_no                   = sa.Column(sa.Unicode(13), nullable=True)
    template_code                = sa.Column(sa.Unicode(10), nullable=True)
    data                         = sa.Column(sa.Unicode(4000), nullable=False)
    issued_at                    = sa.Column(sa.DateTime(), nullable=True)

    fdc_side_order               = orm.relationship('FDCSideOrder', backref='fdc_side_tickets')

    def to_dict(self):
        return dict(
            type=self.type,
            barcode_no=self.barcode_no,
            template_code=self.template_code,
            data=self.data
            )


class FDCSideOrder(Base):
    __tablename__ = 'FDCSideOrder'

    id                           = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    store_code                   = sa.Column(sa.Unicode(6), nullable=True)
    mmk_no                       = sa.Column(sa.Unicode(1), nullable=True)
    type                         = sa.Column(sa.Integer, nullable=False)
    order_id                     = sa.Column(sa.Unicode(12), nullable=False)
    barcode_no                   = sa.Column(sa.Unicode(13), nullable=False)
    exchange_no                  = sa.Column(sa.Unicode(13), nullable=True)
    client_code                  = sa.Column(sa.Unicode(24), nullable=False)
    total_amount                 = sa.Column(sa.Numeric(precision=16, scale=0), nullable=False)
    ticket_payment               = sa.Column(sa.Numeric(precision=9, scale=0), nullable=False)
    ticketing_fee                = sa.Column(sa.Numeric(precision=8, scale=0), nullable=False)
    system_fee                   = sa.Column(sa.Numeric(precision=8, scale=0), nullable=False)
    kogyo_name                   = sa.Column(sa.Unicode(40), nullable=False)
    koen_date                    = sa.Column(sa.DateTime(), nullable=False)

    ticketing_start_at           = sa.Column(sa.DateTime(), nullable=True)
    ticketing_end_at             = sa.Column(sa.DateTime(), nullable=True)

    paid_at                      = sa.Column(sa.DateTime(), nullable=True)
    issued_at                    = sa.Column(sa.DateTime(), nullable=True)

    voided_at                    = sa.Column(sa.DateTime(), nullable=True)

    payment_sheet_text           = sa.Column(sa.Unicode(490), nullable=True)

    @property
    def valid_barcode_no(self):
        if self.type == 1:
            if self.paid_at is None and self.issued_at is None:
                return self.barcode_no
        elif self.type == 2:
            if self.paid_at is None:
                return self.barcode_no
            elif self.issued_at is None:
                return self.exchange_no
        elif self.type == 3:
            if self.issued_at is None:
                return self.barcode_no
        elif self.type == 4:
            if self.paid_at is None:
                return self.barcode_no
        return None

    def to_dict(self):
        return dict( 
            id=self.id,
            store_code=self.store_code,
            mmk_no=self.mmk_no,
            type=self.type,
            order_id=self.order_id,
            barcode_no=self.barcode_no,
            exchange_no=self.exchange_no,
            valid_barcode_no=self.valid_barcode_no,
            client_code=self.client_code,
            total_amount=self.total_amount,
            ticket_payment=self.ticket_payment,
            ticketing_fee=self.ticketing_fee,
            system_fee=self.system_fee,
            kogyo_name=self.kogyo_name,
            koen_date=self.koen_date,
            ticketing_start_at=self.ticketing_start_at,
            ticketing_end_at=self.ticketing_end_at,
            paid_at=self.paid_at,
            issued_at=self.issued_at,
            tickets=[ticket.to_dict() for ticket in self.fdc_side_tickets]
            )
