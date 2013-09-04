from zope.interface import Interface

class ISalesSegmentQueryable(Interface):
    def query_sales_segment(user, now, type):
        pass
