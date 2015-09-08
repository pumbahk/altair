import logging
from sqlalchemy.sql.expression import and_, or_
from sqlalchemy.sql import func
from .models import (
    FamiPortOrder,
    FamiPortOrderType,
    FamiPortReceipt,
    FamiPortReceiptType,
    )
from .exc import (
    FamiPortUnsatisfiedPreconditionError,
    )

logger = logging.getLogger(__name__)

class FamiPortOrderCanceller(object):
    def __init__(self, request, session):
        self.request = request
        self.session = session

    def cancel_one(self, famiport_order, now):
        logger.info('trying to expire FamiPortOrder(id=%ld, order_no=%s)' % (famiport_order.id, famiport_order.order_no))
        should_be_expired_at = famiport_order.expired(now)
        if should_be_expired_at is not None:
            logger.info('FamiPortOrder(id=%ld, order_no=%s) should be (have been) expired at %s' % (famiport_order.id, famiport_order.order_no, should_be_expired_at))
            if famiport_order.automatically_cancellable:
                try:
                    famiport_order.mark_canceled(now, self.request)
                except FamiPortUnsatisfiedPreconditionError:
                    logger.exception('temporary failure; try to expire it later')
                    return
            famiport_order.mark_expired(now, self.request)

    def __call__(self, now):
        famiport_order_ids = self.session.query(FamiPortOrder.id, FamiPortOrder.type) \
            .join(FamiPortOrder.famiport_receipts) \
            .filter(
                FamiPortOrder.invalidated_at.is_(None),
                FamiPortOrder.canceled_at.is_(None),
                FamiPortOrder.expired_at.is_(None),
                FamiPortReceipt.canceled_at.is_(None),
                FamiPortReceipt.completed_at.is_(None),
                or_(
                    and_(
                        FamiPortReceipt.type == FamiPortReceiptType.CashOnDelivery.value,
                        or_(
                            FamiPortOrder.payment_due_at < now,
                            FamiPortOrder.ticketing_end_at < now
                            )
                        ),
                    and_(
                        FamiPortReceipt.type == FamiPortReceiptType.Payment.value,
                        FamiPortOrder.payment_due_at < now,
                        ),
                    and_(
                        FamiPortReceipt.type == FamiPortReceiptType.Ticketing.value,
                        FamiPortOrder.ticketing_end_at < now
                        )
                    )
                ) \
            .distinct() \
            .all()
        for famiport_order_id, _ in famiport_order_ids:
            famiport_order = self.session.query(FamiPortOrder).filter_by(id=famiport_order_id).one()
            self.cancel_one(famiport_order, now)
            self.session.commit()

