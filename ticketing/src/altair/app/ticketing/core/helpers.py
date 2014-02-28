from datetime import datetime

__all__ = [
    'build_sales_segment_list_for_inner_sales',
    ]

def build_sales_segment_list_for_inner_sales(sales_segments, now=None):
    if now is None:
        now = datetime.now()
    def sales_segment_sort_key_func(ss):
        return (
            ss.kind == u'sales_counter',
            ss.start_at is None or ss.start_at <= now,
            ss.end_at is None or now <= ss.end_at,
            -ss.start_at.toordinal() if ss.start_at else 0,
            ss.id
            )
    return sorted(sales_segments, key=sales_segment_sort_key_func, reverse=True)
