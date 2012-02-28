import unittest
from calendar_stream import YearStream
from calendar_stream import MonthStream
from calendar_stream import DayStream
from calendar_stream import YearE
from calendar_stream import MonthE



class ElementStartEndTest(unittest.TestCase):
    def _makeEnv(self, by, bm, bd, ay, am, ad):
        env = {}
        env["start_date"] = by, bm, bd
        env["end_date"] = ay, am, ad
        return env
    
    def test_yearE_is_start(self):
        env = self._makeEnv(2011, 7, 8, 2013, 2, 3)
        self.assertTrue(YearE(2011, env).is_start)
        self.assertFalse(YearE(2012, env).is_start)
        self.assertFalse(YearE(2013, env).is_start)

    def test_yearE_is_end(self):
        env = self._makeEnv(2011, 7, 8, 2013, 2, 3)
        self.assertFalse(YearE(2011, env).is_end)
        self.assertFalse(YearE(2012, env).is_end)
        self.assertTrue(YearE(2013, env).is_end)

    def test_monthE_is_start_with_start_year(self):
        env = self._makeEnv(2011, 7, 8, 2013, 2, 3)
        ye = YearE(2011, env)
        self.assertFalse(MonthE(ye, 6, env).is_start)
        self.assertTrue(MonthE(ye, 7, env).is_start)
        self.assertFalse(MonthE(ye, 8, env).is_start)

    def test_monthE_is_start_with_non_start_year(self):
        env = self._makeEnv(2011, 7, 8, 2013, 2, 3)
        ye = YearE(2012, env)
        self.assertFalse(MonthE(ye, 6, env).is_start)
        self.assertFalse(MonthE(ye, 7, env).is_start)
        self.assertFalse(MonthE(ye, 8, env).is_start)

    def test_monthE_is_start_with_end_year(self):
        env = self._makeEnv(2011, 7, 8, 2013, 2, 3)
        ye = YearE(2013, env)
        self.assertFalse(MonthE(ye, 6, env).is_start)
        self.assertFalse(MonthE(ye, 7, env).is_start)
        self.assertFalse(MonthE(ye, 8, env).is_start)

    def test_monthE_is_end_with_start_year(self):
        env = self._makeEnv(2011, 7, 8, 2013, 2, 3)
        ye = YearE(2011, env)
        self.assertFalse(MonthE(ye, 1, env).is_end)
        self.assertFalse(MonthE(ye, 2, env).is_end)
        self.assertFalse(MonthE(ye, 3, env).is_end)

    def test_monthE_is_end_with_non_start_year(self):
        env = self._makeEnv(2011, 7, 8, 2013, 2, 3)
        ye = YearE(2012, env)
        self.assertFalse(MonthE(ye, 1, env).is_end)
        self.assertFalse(MonthE(ye, 2, env).is_end)
        self.assertFalse(MonthE(ye, 3, env).is_end)

    def test_monthE_is_end_with_end_year(self):
        env = self._makeEnv(2011, 7, 8, 2013, 2, 3)
        ye = YearE(2013, env)
        self.assertFalse(MonthE(ye, 1, env).is_end)
        self.assertTrue(MonthE(ye, 2, env).is_end)
        self.assertFalse(MonthE(ye, 3, env).is_end)


class ElementTermTest(unittest.TestCase):
    def _makeEnv(self, by, bm, bd, ay, am, ad):
        env = {}
        env["start_date"] = by, bm, bd
        env["end_date"] = ay, am, ad
        return env

    def test_year_term(self):
        env = self._makeEnv(2011, 7, 8, 2013, 2, 3)
        self.assertEquals(YearStream(env).years(), 
                          [2011, 2012, 2013])

    def test_month_term_is_start(self):
        env = self._makeEnv(2011, 7, 8, 2013, 2, 3)
        ye = YearE(2011, env)
        self.assertEquals(MonthStream(ye).months(), 
                          [7, 8, 9, 10, 11, 12])

    def test_month_term_in_middle(self):
        env = self._makeEnv(2011, 7, 8, 2013, 2, 3)
        ye = YearE(2012, env)
        self.assertEquals(MonthStream(ye).months(), 
                          [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        
    def test_month_term_is_end(self):
        env = self._makeEnv(2011, 7, 8, 2013, 2, 3)
        ye = YearE(2013, env)
        self.assertEquals(MonthStream(ye).months(), 
                          [1, 2])

    def test_day_term_is_start_before_month(self):
        pass
    """ inivalid return value. but this situation is not occured.
    """
        ## todo:follow

    def test_day_term_is_start(self):
        env = self._makeEnv(2011, 7, 8, 2013, 2, 3)
        ye = YearE(2011, env)
        me = MonthE(ye, 7, env)
        self.assertEquals(DayStream(me).days(), 
                          [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31])

    def test_day_term_is_start_after_month(self):
        env = self._makeEnv(2011, 7, 8, 2013, 2, 3)
        ye = YearE(2011, env)
        me = MonthE(ye, 8, env)
        self.assertEquals(DayStream(me).days(), 
                          [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31])


    def test_day_term_is_end_before_month(self):
        env = self._makeEnv(2011, 7, 8, 2013, 2, 3)
        ye = YearE(2013, env)
        me = MonthE(ye, 1, env)
        self.assertEquals(DayStream(me).days(), 
                          [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31])


    def test_day_term_is_end(self):
        env = self._makeEnv(2011, 7, 8, 2013, 2, 3)
        ye = YearE(2013, env)
        me = MonthE(ye, 2, env)
        self.assertEquals(DayStream(me).days(), 
                          [1, 2, 3])

    def test_day_term_is_end_after_month(self):
        pass
    """ inivalid return value. but this situation is not occured.
    """
        ## todo:follow

class CStreamFunctionalTest(unittest.TestCase):
    def _make_gen(self):
        from calendar_stream import PackedCalendarStream
        from calendar_stream import CalendarStreamGenerator

        gen = CalendarStreamGenerator(PackedCalendarStream, force_start_from_monday=True)
        s = gen.start_from(2011, 7, 8)
        ys = s.iterate_to(2012, 2, 2)
        return ys

    def test_all_row_start_with_monday(self):
        """ packed stream's row is must start with monday!!
        """
        from datetime import date
        MONDAY = 0
        for r in self._make_gen():
            y, m, d = r[0]
            self.assertEquals(date(y.value, m.value, d.value).weekday(), MONDAY)


    def test_it(self):
        values = []
        for r in self._make_gen():
            values.append([(y.value, m.value, d.value) for y, m, d in r])
        self.assertEquals(values,  self.EXPEXTED)

    EXPEXTED = [[(2011, 7, 4), (2011, 7, 5), (2011, 7, 6), (2011, 7, 7), (2011, 7, 8), (2011, 7, 9), (2011, 7, 10)],
                [(2011, 7, 11), (2011, 7, 12), (2011, 7, 13), (2011, 7, 14), (2011, 7, 15), (2011, 7, 16), (2011, 7, 17)],
                [(2011, 7, 18), (2011, 7, 19), (2011, 7, 20), (2011, 7, 21), (2011, 7, 22), (2011, 7, 23), (2011, 7, 24)],
                [(2011, 7, 25), (2011, 7, 26), (2011, 7, 27), (2011, 7, 28), (2011, 7, 29), (2011, 7, 30), (2011, 7, 31)],
                [(2011, 8, 1), (2011, 8, 2), (2011, 8, 3), (2011, 8, 4), (2011, 8, 5), (2011, 8, 6), (2011, 8, 7)],
                [(2011, 8, 8), (2011, 8, 9), (2011, 8, 10), (2011, 8, 11), (2011, 8, 12), (2011, 8, 13), (2011, 8, 14)],
                [(2011, 8, 15), (2011, 8, 16), (2011, 8, 17), (2011, 8, 18), (2011, 8, 19), (2011, 8, 20), (2011, 8, 21)],
                [(2011, 8, 22), (2011, 8, 23), (2011, 8, 24), (2011, 8, 25), (2011, 8, 26), (2011, 8, 27), (2011, 8, 28)],
                [(2011, 8, 29), (2011, 8, 30), (2011, 8, 31), (2011, 9, 1), (2011, 9, 2), (2011, 9, 3), (2011, 9, 4)],
                [(2011, 9, 5), (2011, 9, 6), (2011, 9, 7), (2011, 9, 8), (2011, 9, 9), (2011, 9, 10), (2011, 9, 11)],
                [(2011, 9, 12), (2011, 9, 13), (2011, 9, 14), (2011, 9, 15), (2011, 9, 16), (2011, 9, 17), (2011, 9, 18)],
                [(2011, 9, 19), (2011, 9, 20), (2011, 9, 21), (2011, 9, 22), (2011, 9, 23), (2011, 9, 24), (2011, 9, 25)],
                [(2011, 9, 26), (2011, 9, 27), (2011, 9, 28), (2011, 9, 29), (2011, 9, 30), (2011, 10, 1), (2011, 10, 2)],
                [(2011, 10, 3), (2011, 10, 4), (2011, 10, 5), (2011, 10, 6), (2011, 10, 7), (2011, 10, 8), (2011, 10, 9)],
                [(2011, 10, 10), (2011, 10, 11), (2011, 10, 12), (2011, 10, 13), (2011, 10, 14), (2011, 10, 15), (2011, 10, 16)],
                [(2011, 10, 17), (2011, 10, 18), (2011, 10, 19), (2011, 10, 20), (2011, 10, 21), (2011, 10, 22), (2011, 10, 23)],
                [(2011, 10, 24), (2011, 10, 25), (2011, 10, 26), (2011, 10, 27), (2011, 10, 28), (2011, 10, 29), (2011, 10, 30)],
                [(2011, 10, 31), (2011, 11, 1), (2011, 11, 2), (2011, 11, 3), (2011, 11, 4), (2011, 11, 5), (2011, 11, 6)],
                [(2011, 11, 7), (2011, 11, 8), (2011, 11, 9), (2011, 11, 10), (2011, 11, 11), (2011, 11, 12), (2011, 11, 13)],
                [(2011, 11, 14), (2011, 11, 15), (2011, 11, 16), (2011, 11, 17), (2011, 11, 18), (2011, 11, 19), (2011, 11, 20)],
                [(2011, 11, 21), (2011, 11, 22), (2011, 11, 23), (2011, 11, 24), (2011, 11, 25), (2011, 11, 26), (2011, 11, 27)],
                [(2011, 11, 28), (2011, 11, 29), (2011, 11, 30), (2011, 12, 1), (2011, 12, 2), (2011, 12, 3), (2011, 12, 4)],
                [(2011, 12, 5), (2011, 12, 6), (2011, 12, 7), (2011, 12, 8), (2011, 12, 9), (2011, 12, 10), (2011, 12, 11)],
                [(2011, 12, 12), (2011, 12, 13), (2011, 12, 14), (2011, 12, 15), (2011, 12, 16), (2011, 12, 17), (2011, 12, 18)],
                [(2011, 12, 19), (2011, 12, 20), (2011, 12, 21), (2011, 12, 22), (2011, 12, 23), (2011, 12, 24), (2011, 12, 25)],
                [(2011, 12, 26), (2011, 12, 27), (2011, 12, 28), (2011, 12, 29), (2011, 12, 30), (2011, 12, 31), (2012, 1, 1)],
                [(2012, 1, 2), (2012, 1, 3), (2012, 1, 4), (2012, 1, 5), (2012, 1, 6), (2012, 1, 7), (2012, 1, 8)],
                [(2012, 1, 9), (2012, 1, 10), (2012, 1, 11), (2012, 1, 12), (2012, 1, 13), (2012, 1, 14), (2012, 1, 15)],
                [(2012, 1, 16), (2012, 1, 17), (2012, 1, 18), (2012, 1, 19), (2012, 1, 20), (2012, 1, 21), (2012, 1, 22)],
                [(2012, 1, 23), (2012, 1, 24), (2012, 1, 25), (2012, 1, 26), (2012, 1, 27), (2012, 1, 28), (2012, 1, 29)],
                [(2012, 1, 30), (2012, 1, 31), (2012, 2, 1), (2012, 2, 2), (2012, 2, 3), (2012, 2, 4), (2012, 2, 5)]]

if __name__ == "__main__":
    unittest.main()
