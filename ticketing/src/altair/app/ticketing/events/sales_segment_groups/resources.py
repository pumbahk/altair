def sync_attr(dest, src, attr):
    setattr(dest, attr, getattr(src, attr))

class SalesSegmentGroupUpdate(object):

    def __init__(self, sales_segment_group):
        self.ssg = sales_segment_group

    def update(self, sales_segments):
        for ss in sales_segments:
            self.update_sales_segment(ss)

    def update_sales_segment(self, ss):
        if ss.use_default_seat_choice:
            sync_attr(ss, self.ssg, 'seat_choice')
        if ss.use_default_public:
            sync_attr(ss, self.ssg, 'public')
        if ss.use_default_reporting:
            sync_attr(ss, self.ssg, 'reporting')
        if ss.use_default_payment_delivery_method_pairs:
            sync_attr(ss, self.ssg, 'payment_delivery_method_pairs')
        if ss.use_default_start_at:
            sync_attr(ss, self.ssg, 'start_at')
        if ss.use_default_end_at:
            sync_attr(ss, self.ssg, 'end_at')
        if ss.use_default_upper_limit:
            sync_attr(ss, self.ssg, 'upper_limit')
        if ss.use_default_order_limit:
            sync_attr(ss, self.ssg, 'order_limit')
        if ss.use_default_account_id:
            sync_attr(ss, self.ssg, 'account_id')
        if ss.use_default_margin_ratio:
            sync_attr(ss, self.ssg, 'margin_ratio')
        if ss.use_default_refund_ratio:
            sync_attr(ss, self.ssg, 'refund_ratio')
        if ss.use_default_printing_fee:
            sync_attr(ss, self.ssg, 'printing_fee')
        if ss.use_default_registration_fee:
            sync_attr(ss, self.ssg, 'registration_fee')
        if ss.use_default_auth3d_notice:
            sync_attr(ss, self.ssg, 'auth3d_notice')

