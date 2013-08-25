from altair.app.ticketing.core.models import SalesSegment

def sync_attr(dest, src, attr):
    setattr(dest, attr, getattr(src, attr))

class SalesSegmentGroupCreate(object):
    def __init__(self, new_sales_segment_group):
        self.ssg = new_sales_segment_group

    def create(self, performances):
        for p in performances:
            self.create_sales_segment_for(p)

    def create_sales_segment_for(self, performance):
        ss = SalesSegment(
            organization=performance.event.organization,
            event=performance.event,
            performance=performance,
            sales_segment_group=self.ssg,
            use_default_seat_choice=True,
            use_default_public=True,
            use_default_reporting=True,
            use_default_payment_delivery_method_pairs=True,
            use_default_start_at=True,
            use_default_end_at=True,
            use_default_upper_limit=True,
            use_default_order_limit=True,
            use_default_account_id=True,
            use_default_margin_ratio=True,
            use_default_refund_ratio=True,
            use_default_printing_fee=True,
            use_default_registration_fee=True,
            use_default_auth3d_notice=True,
            )
        update_sales_segment(self.ssg, ss)
        return ss
            
class SalesSegmentGroupUpdate(object):

    def __init__(self, sales_segment_group):
        self.ssg = sales_segment_group

    def update(self, sales_segments):
        for ss in sales_segments:
            update_sales_segment(self.ssg, ss)

def update_sales_segment(ssg, ss):
    if ss.use_default_seat_choice:
        sync_attr(ss, ssg, 'seat_choice')
    if ss.use_default_public:
        sync_attr(ss, ssg, 'public')
    if ss.use_default_reporting:
        sync_attr(ss, ssg, 'reporting')
    if ss.use_default_payment_delivery_method_pairs:
        sync_attr(ss, ssg, 'payment_delivery_method_pairs')
    if ss.use_default_start_at:
        sync_attr(ss, ssg, 'start_at')
    if ss.use_default_end_at:
        sync_attr(ss, ssg, 'end_at')
    if ss.use_default_upper_limit:
        sync_attr(ss, ssg, 'upper_limit')
    if ss.use_default_order_limit:
        sync_attr(ss, ssg, 'order_limit')
    if ss.use_default_account_id:
        sync_attr(ss, ssg, 'account_id')
    if ss.use_default_margin_ratio:
        sync_attr(ss, ssg, 'margin_ratio')
    if ss.use_default_refund_ratio:
        sync_attr(ss, ssg, 'refund_ratio')
    if ss.use_default_printing_fee:
        sync_attr(ss, ssg, 'printing_fee')
    if ss.use_default_registration_fee:
        sync_attr(ss, ssg, 'registration_fee')
    if ss.use_default_auth3d_notice:
        sync_attr(ss, ssg, 'auth3d_notice')

