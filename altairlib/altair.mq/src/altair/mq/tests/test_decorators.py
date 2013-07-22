import unittest
import mock

class task_configTests(unittest.TestCase):
    def _getTarget(self):
        from ..decorators import task_config
        return task_config

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)


    def test_it(self):
        root_factory = mock.Mock()
        target = self._makeOne(
            root_factory=root_factory,
            queue="testing",
            passive=True,
            durable=True, 
            exclusive=True, 
            auto_delete=True,
            nowait=True,
            arguments=object(),
        )
        
        self.assertEqual(target.root_factory, root_factory)
