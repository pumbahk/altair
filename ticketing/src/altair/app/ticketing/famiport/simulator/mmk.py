import sqlalchemy as sa
from sqlalchemy.sql import func as sqlf

class MmkSequence(object):
    def __init__(self, metadata, bind):
        self.metadata = metadata
        self.bind = bind
        self.mmk_sequence = sa.Table(
            'MmkSequence',
            self.metadata,
            sa.Column('seq', sa.Integer(primary_key=True, nullable=False)),
            sa.Column('date', sa.Date(), nullable=False),
            sa.Column('store_code', sa.Unicode(7), nullable=False)
            )
        self.metadata.create_all(bind)

    def next_serial(self, now, store_code):
        now = now.date()
        with self.bind.begin() as conn:
            conn.execute(self.mmk_sequence.insert().values(date=now, store_code=store_code))
            v, = conn.execute(sa.select([sqlf.count()], from_obj=self.mmk_sequence).where(self.mmk_sequence.c.date == now).where(self.mmk_sequence.c.store_code == store_code)).fetchone()
        return v
