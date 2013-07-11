# -*- coding:utf-8 -*-
import logging

logger = logging.getLogger(__name__)

class LotCloser(object):
    def __init__(self, lot, request):
        self.request = request
        self.lot = lot


    def close(self):
        for entry in self.lot.remained_entries:
            logger.debug('close {0}'.format(entry.entry_no))
            entry.close()

        # 終了状態でフラグ管理
        self.lot.finish_lotting()
        logger.info('close lot id={0}'.format(self.lot.id))

    def can_close(self):
        """ 申込中の状態が残ってたらクローズできない
        二回クローズしない
        """
        return (not self.lot.query_receipt_entries.count()
                and not self.lot.is_finished())
