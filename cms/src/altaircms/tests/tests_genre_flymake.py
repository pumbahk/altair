from altaircms.testing import setup_db
from altaircms.testing import teardown_db

def setUpModule():
    setup_db(models=[
            "altaircms.models", 
            "altaircms.page.models", 
            "altaircms.event.models", 
            ])

def tearDownModule():
    teardown_db()
import unittest

class AncestorsTests(unittest.TestCase):
    def _getTarget(self):
        from altaircms.models import Genre
        return Genre

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def tearDown(self):
        import transaction
        transaction.abort()

    def test_self_only(self):
        from altaircms.models import DBSession

        music = self._makeOne(name="music")
        DBSession.add(music)
        self.assertEqual(music.ancestors, [])

    def test_have_parent(self):
        from altaircms.models import DBSession

        music = self._makeOne(name="music")
        jpop = self._makeOne(name="music.jpop")
        jpop.add_relation(music, 1)

        DBSession.add(jpop)
        DBSession.flush()
        self.assertEqual(jpop.ancestors, [music])

    def test_has_grand_parent(self):
        from altaircms.models import DBSession

        music = self._makeOne(name="music")
        jpop = self._makeOne(name="music.jpop")
        major = self._makeOne(name="music.jpop.major")

        jpop.add_relation(music, 1)
        major.add_relation(jpop, 1)
        major.add_relation(music, 2)

        DBSession.add(major)
        DBSession.flush()
        self.assertEqual(jpop.ancestors, [music])
        self.assertEqual(major.ancestors, [jpop, music])

    def test_add_parent_multiple(self):
        from altaircms.models import DBSession

        music = self._makeOne(name="music")
        jpop = self._makeOne(name="music.jpop")

        jpop.add_relation(music, 1)
        DBSession.add(jpop)
        DBSession.flush()

        self.assertEqual(jpop.ancestors, [music])

        jpop = DBSession.merge(jpop)
        music = DBSession.merge(music)
        jpop.add_relation(music, 1)
        DBSession.flush()
        self.assertEqual(jpop.ancestors, [music])

    def test_add_remove_add(self):
        from altaircms.models import DBSession

        music = self._makeOne(name="music")
        jpop = self._makeOne(name="music.jpop")

        ## add
        jpop.add_relation(music, 1)
        DBSession.add(jpop)
        DBSession.flush()
        self.assertEqual(jpop.ancestors, [music])

        ## remove
        jpop = DBSession.merge(jpop)
        music = DBSession.merge(music)
        jpop.remove_relation(music)
        DBSession.flush()
        self.assertEqual(jpop.ancestors, [])

        ## add
        jpop.add_relation(music, 1)
        DBSession.flush()
        self.assertEqual(jpop.ancestors, [music])

    def test_add_update(self):
        from altaircms.models import DBSession

        music = self._makeOne(name="music")
        jpop = self._makeOne(name="music.jpop")

        ## add
        jpop.add_relation(music, 1)
        DBSession.add(jpop)
        DBSession.flush()
        self.assertEqual(jpop.ancestors, [music])

        ## remove
        jpop = DBSession.merge(jpop)
        music = DBSession.merge(music)
        jpop.update_relation(music, 10)
        DBSession.flush()
        self.assertEqual(jpop.ancestors, [music])

    def test_query_children(self):
        from altaircms.models import DBSession

        t = self._makeOne(name="music")
        jpop = self._makeOne(name="music.jpop")
        major = self._makeOne(name="music.jpop.major")

        jpop.add_relation(music, 1)
        major.add_relation(jpop, 1)
        major.add_relation(music, 2)

        DBSession.add(major)
        DBSession.flush()
        self.assertEqual(jpop.ancestors, [music])
        self.assertEqual(major.ancestors, [jpop, music])

        self.assertEqual(music.query_children(hop=2).all(), [jpop, major])

if __name__ == "__main__":
    unittest.main()
