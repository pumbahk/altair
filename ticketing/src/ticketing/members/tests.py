import unittest

class CreateLoginUserTests(unittest.TestCase):
    def _getTarget(self):
        from ticketing.members.api import UserForLoginCartBuilder
        return UserForLoginCartBuilder

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args,**kwargs)

    def test_it(self):
        

if __name__ == "__main__":
    unittest.main()
