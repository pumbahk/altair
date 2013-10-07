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
        jpop.add_parent(music, 1)

        DBSession.add(jpop)
        DBSession.flush()
        self.assertEqual(jpop.ancestors, [music])

    def test_has_grand_parent(self):
        from altaircms.models import DBSession

        music = self._makeOne(name="music")
        jpop = self._makeOne(name="music.jpop")
        major = self._makeOne(name="music.jpop.major")

        jpop.add_parent(music, 1)
        major.add_parent(jpop, 1)
        major.add_parent(music, 2)

        DBSession.add(major)
        DBSession.flush()
        self.assertEqual(jpop.ancestors, [music])
        self.assertEqual(major.ancestors, [jpop, music])

    def test_add_parent_multiple(self):
        from altaircms.models import DBSession

        music = self._makeOne(name="music")
        jpop = self._makeOne(name="music.jpop")

        jpop.add_parent(music, 1)
        DBSession.add(jpop)
        DBSession.flush()

        self.assertEqual(jpop.ancestors, [music])

        jpop = DBSession.merge(jpop)
        music = DBSession.merge(music)
        jpop.add_parent(music, 1)
        DBSession.flush()
        self.assertEqual(jpop.ancestors, [music])

    def test_add_remove_add(self):
        from altaircms.models import DBSession

        music = self._makeOne(name="music")
        jpop = self._makeOne(name="music.jpop")

        ## add
        jpop.add_parent(music, 1)
        DBSession.add(jpop)
        DBSession.flush()
        self.assertEqual(jpop.ancestors, [music])

        ## remove
        jpop = DBSession.merge(jpop)
        music = DBSession.merge(music)
        jpop.remove_parent(music)
        DBSession.flush()
        self.assertEqual(jpop.ancestors, [])

        ## add
        jpop.add_parent(music, 1)
        DBSession.flush()
        self.assertEqual(jpop.ancestors, [music])

    def test_add_update(self):
        from altaircms.models import DBSession

        music = self._makeOne(name="music")
        jpop = self._makeOne(name="music.jpop")

        ## add
        jpop.add_parent(music, 1)
        DBSession.add(jpop)
        DBSession.flush()
        self.assertEqual(jpop.ancestors, [music])

        ## remove
        jpop = DBSession.merge(jpop)
        music = DBSession.merge(music)
        jpop.update_parent(music, 10)
        DBSession.flush()
        self.assertEqual(jpop.ancestors, [music])

    @unittest.skip ("* #5609: must fix")
    def test_query_children(self):
        from altaircms.models import DBSession

        top = self._makeOne(name="top")
        child = self._makeOne(name="top.child")
        grand_child = self._makeOne(name="top.child.grand_child")
        grand_child2 = self._makeOne(name="top.child.grand_child2")

        child.add_parent(top, 1)
        grand_child.add_parent(child, 1)
        grand_child.add_parent(top, 2)
        grand_child2.add_parent(child, 1)
        grand_child2.add_parent(top, 2)
        DBSession.add(grand_child)
        DBSession.add(grand_child2)
        DBSession.flush()

        self.assertEqual(top.children, [child])
        self.assertEqual(child.children, [grand_child, grand_child2])
        self.assertEqual(sorted(top.query_descendant().all()), sorted([child, grand_child, grand_child2]))

if __name__ == "__main__":
    unittest.main()
