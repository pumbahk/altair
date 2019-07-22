# coding=utf-8
from altair.app.ticketing.cooperation.rakuten_live.utils import convert_type
from standardenum import StandardEnum

import sqlalchemy as sa

from altair.app.ticketing.models import Base, BaseModel
from altair.models import WithTimestamp, LogicallyDeleted, Identifier


class RakutenLiveStatus(StandardEnum):
    """Enum Class for the status representing if Order or LotEntry data has sent to R-Live."""
    UNSENT = 0  # R-Liveに予約または申込データが送られていない
    SENT = 1  # R-Liveに予約または申込データが送られた


class RakutenLiveSession(object):
    """Class stored in request session to store R-Live data."""
    def __init__(self, user_id=None, stream_id=None, channel_id=None, slug=None, product_id=None, **kwargs):
        self.user_id = user_id
        self.stream_id = stream_id
        self.channel_id = channel_id
        self.slug = slug
        self.product_id = product_id
        self._performance_id = kwargs.get('performance_id', None)
        self._lot_id = kwargs.get('lot_id', None)

    @property
    def performance_id(self):
        return convert_type(self._performance_id, int)

    @property
    def lot_id(self):
        return convert_type(self._lot_id, int)

    def as_model(self, order_entry_no=None, status=int(RakutenLiveStatus.UNSENT)):
        return RakutenLiveRequest(
            order_entry_no=order_entry_no,
            live_user_id=convert_type(self.user_id, int),
            live_stream_id=convert_type(self.stream_id, int),
            live_channel_id=convert_type(self.channel_id, int),
            live_slug=convert_type(self.slug, str),
            live_product_id=convert_type(self.product_id, int),
            status=status
        )

    def as_dict(self):
        return {
            'user_id': convert_type(self.user_id, int),
            'stream_id': convert_type(self.stream_id, int),
            'channel_id': convert_type(self.channel_id, int),
            'slug': convert_type(self.slug, str),
            'product_id': convert_type(self.product_id, int),
        }


class RakutenLiveRequest(Base, BaseModel, WithTimestamp, LogicallyDeleted):
    """
    Model Class for RakutenLiveRequest table.
    See: https://confluence.rakuten-it.com/confluence/display/TKT/Outline+of+Development
    """
    __tablename__ = 'RakutenLiveRequest'

    id = sa.Column(Identifier, primary_key=True)
    order_entry_no = sa.Column(sa.Unicode(255))  # order_no or entry_no
    live_user_id = sa.Column(sa.Integer)  # R-Live User ID
    live_stream_id = sa.Column(sa.Integer)  # Liveストリーミングを特定するID
    live_channel_id = sa.Column(sa.Integer)  # Liveストリーミングを特定する英数字のID
    live_slug = sa.Column(sa.Unicode(255))  # ユーザが参加しているチャンネルのID
    live_product_id = sa.Column(sa.Integer)  # Product ID in Rakuten Live CMS
    status = sa.Column(sa.SmallInteger)  # データがR-Liveに送信されたかどうかを示すステータス (RakutenLiveStatus Enum)

    @property
    def is_sendable_state(self):
        if self.status != int(RakutenLiveStatus.UNSENT):
            return False

        required_data = (
            self.order_entry_no,
            self.live_user_id,
            self.live_stream_id,
            self.live_channel_id,
            self.live_slug,
            self.live_product_id,
        )
        return all([d is not None and d != u'' for d in required_data])
