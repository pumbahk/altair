#-*- coding: utf-8 -*-
from altair.augus.protocols.common import (
    RecordIF,
    ProtocolBase,
    )
from altair.augus.protocols.venue import (    
    VenueSyncRequestRecord,
    VenueSyncRequest,
    )

class AltairAugusVenueSyncRequestAttribute(object):
    pass

class AltairAugusVenueSyncRequestRecord(RecordIF, AltairAugusVenueSyncRequestAttribute):
    attributes = [
        'id_',
        'name',
        'seat_no',
        'l0_id',
        'group_l0_id',
        'row_l0_id',
        ] + map(lambda name: 'augus_' + name, VenueSyncRequestRecord.attributes)

class AltairAugusVenueSyncRequest(ProtocolBase):
    record = AltairAugusVenueSyncRequestRecord
