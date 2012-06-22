
import sqlahelper
import sqlalchemy as sa

Base = sqlahelper.get_base()
DBSession = sqlahelper.get_session()

class ReservedNumber(Base):
    __tablename__ = "reserved_number"
    query = DBSession.query_property()
    id = sa.Column(sa.Integer, primary_key=True)
    order_no = sa.Column(sa.Unicode(255), unique=True)
    number = sa.Column(sa.Unicode(32))


class PaymentReservedNumber(Base):
    __tablename__ = "payment_reserved_number"
    query = DBSession.query_property()
    id = sa.Column(sa.Integer, primary_key=True)
    order_no = sa.Column(sa.Unicode(255), unique=True)
    number = sa.Column(sa.Unicode(32))
