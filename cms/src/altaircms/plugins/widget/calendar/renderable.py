from calendar_stream import PackedCalendarStream
from calendar_stream import CalendarStreamGenerator

__all__ = ["CalendarOutput"]

YEAR, MONTH, DAY = [0, 1, 2]
FIRST, LAST = [0, -1]

class CalendarWeek(object):
    def __init__(self, r, performances, month_changed=False):
        self.month_changed = month_changed or r[FIRST][MONTH].value != r[LAST][MONTH].value
        self.month = r[LAST][MONTH].value
        self.year = r[LAST][YEAR].value
        self.r = r
        self.week = []
        self.performances = performances

    WDAYCLASS_MAP = [["first"], 
                     [],
                     [],
                     [],
                     [],
                     ["saturday"],
                     ["last", "holiday"]]

    def __iter__(self):
        for day_class_base, (y, m, d) in zip(self.WDAYCLASS_MAP, self.r):
            day_class = day_class_base[:]
            day_class.append("odd_month" if m.value % 2 == 1 else "even_month")
            yield {"day_class": " ".join(day_class),
                   "day": d.value, 
                   "performance": self.performances.get(d.value, [])
                   }
    """
    * start of week: first
    * end of week: last
    * in saturday: saturday
    * in holiday(include sunday): holiday
    
    odd month: odd_month
    even month: even_month
    
    if change month durning rendeering a row, putting special th element before rendering.
    """

class CalendarOutput(object):
    template = None

    def __init__(self, performances=None, template=None):
        self.template = template or self.template
        self.performances = performances or {}
        
    def each_rows(self, begin_date, end_date):
        gen = CalendarStreamGenerator(PackedCalendarStream, force_start_from_monday=True)
        stream = gen.start_from(begin_date.year, begin_date.month, begin_date.day)
        itr = stream.iterate_to(end_date.year, end_date.month, end_date.day)
        yield CalendarWeek(itr.next(), self.performances, month_changed=True)
        for r in itr:
            yield CalendarWeek(r, self.performances)

    def render(self, begin_date, end_date):
        rows = self.each_rows(begin_date, end_date)
        return self.template.render_unicode(cal=rows)

if __name__ == "__main__":
    import mako.template
    template = mako.template.Template(filename="rakuten.calendar.mako",
                                      input_encoding='utf-8', 
                                      output_encoding="utf-8")
    from datetime import date
    cal = CalendarOutput()
    print template.render_unicode(
        cal=cal.each_rows(date(2012, 2, 6), date(2012, 3, 18)))
