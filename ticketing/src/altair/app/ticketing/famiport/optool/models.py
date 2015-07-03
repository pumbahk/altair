# encoding: utf-8

import sqlalchemy as sa
from altair.models import Identifier
from ..models import Base, FamiPortRefund, FamiPortRefundEntry, FamiPortTicket, FamiPortShop

class FamiPortOperator(Base):
    __tablename__ = 'FamiPortOperator'

    id = sa.Column(Identifier, primary_key=True, nullable=False, autoincrement=True)
    user_name = sa.Column(sa.Unicode(32), nullable=False, unique=True)
    password = sa.Column(sa.Unicode(96), nullable=False)
    role = sa.Column(sa.Unicode(32), nullable=False)

class RefundTicketSearchResultRow(Base):
    __table__ = sa.Table('RefundTicketSearchResultRow', sa.MetaData(bind=None),
                        sa.Column('id', sa.Integer, primary_key=True),
                        sa.Column('refund_status', sa.Unicode(1)),
                        sa.Column('district_code', sa.String(2)),
                        sa.Column('refunded_branch_code', sa.Integer(3)),
                        sa.Column('issued_shop_code', sa.String(5)),
                        sa.Column('issued_branch_name', sa.Unicode(40)),
                        sa.Column('management_number', sa.Integer(9)),
                        sa.Column('barcode_number', sa.String(13)),
                        sa.Column('event_code', sa.String(6)),
                        sa.Column('event_subcode', sa.String(4)),
                        sa.Column('performance_date', sa.Date()),
                        sa.Column('event_name', sa.Unicode(80)),
                        sa.Column('refunded_amount', sa.DECIMAL(9, 0)),
                        sa.Column('refunded_at', sa.DateTime()),
                        sa.Column('refunded_shop_code', sa.String(5)),
                        sa.Column('issued_branch_name', sa.Unicode(40)),
                        # sa.ForeignKeyConstraint() # TODO barcode_number, event_code, event_subcode
                        )