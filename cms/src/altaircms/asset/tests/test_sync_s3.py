import unittest
from pyramid import testing
import os.path
from collections import namedtuple

File = namedtuple("File", "name")

class DummyAsset(object):
    def __init__(self, filepath):
        self.filepath = filepath
        self.file_url = None
        self.called_all_files_candidates = False

    def all_files_candidates(self):
        self.called_all_files_candidates = True
        return []

class DummyFileSession(object):
    """for testing"""
    def __init__(self, prefix="", marker=None, make_path=None, **kwargs):
        self.marker = marker
        self.make_path = make_path or (lambda : os.path.abspath(prefix))
        self.added = []
        self.deleted = []
        self.options = {}

    def add(self, o):
        self.added.append(o)

    def delete(self, o):
        self.deleted.append(o)

    def commit(self, extra_args=None):
        return {"create": self.added, "delete": self.deleted, "extra_args": extra_args}

class DummyS3Utility(object):
    @classmethod
    def from_settings(cls, settings):
        return cls()

    def setup(self, config):
        config.add_subscriber(
            self.assert_action, 
            "altaircms.filelib.adapts.AfterCommit")

class SyncS3Tests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.registry.settings.update({
                "altaircms.filesession": DummyFileSession, 
                "altaircms.asset.storepath": ".", 
                })
        self.config.include("altaircms.filelib")
        self.config.include("altaircms.asset.install_filesession")

    def tearDown(self):
        testing.tearDown()

    def assert_interface(self, interface, obj):
        from zope.interface.verify import verifyObject
        self.assertTrue(verifyObject(interface, obj))

    def get_filesession(self):
        from altaircms.asset.creation import get_asset_filesession
        return get_asset_filesession(self.config)
        
    def test_filesession_registered(self):       
        from altaircms.filelib.interfaces import IFileSession
        session = self.get_filesession()
        self.assert_interface(IFileSession, session)
        
    def test_filesession_commit_then_event_is_notified(self):
        _result = object()
        _called = [False]
        matcher = self
        class MyUtility(DummyS3Utility):
            def assert_action(self, event):
                matcher.assertEquals(event.result["extra_args"], _result)
                _called[0] = True

        self.config.registry.settings.update({
                "altaircms.s3.utility": MyUtility
                })
        self.config.include("altaircms.install_upload_file")
        
        session = self.get_filesession()
        session.commit(extra_args=_result)
        self.assertTrue(_called[0])



    S3_Setting = {"s3.access_key": "xxx", 
                  "s3.secret_key": "xxx", 
                  "s3.bucket_name": "xxx"}

    def test_file_is_upload_with_s3utility(self):
        from altaircms.filelib.s3 import S3ConnectionFactory
        uploaded = []
        class Dummy(S3ConnectionFactory):
            def upload(self, f, realpath, options=None):
                uploaded.append((f, realpath))

        self.config.registry.settings.update({"altaircms.s3.utility": Dummy})
        self.config.registry.settings.update(self.S3_Setting)
        self.config.include("altaircms.install_upload_file")
        
        session = self.get_filesession()
        session.add(("test-file", "test-data"),)
        session.commit()

        self.assertEqual(uploaded, [("test-file", "test-data"), ])

    def test_event_is_notified_after_s3upload_with_s3utility(self):
        from altaircms.filelib.s3 import S3ConnectionFactory

        class Dummy(S3ConnectionFactory):
            def upload(self, f, realpath, options=None):
                pass

        _result = object()
        _called = [False]
        matcher = self
        def assert_action(event):
            matcher.assertEquals(event.extra_args, _result)
            _called[0] = True

        self.config.registry.settings.update({"altaircms.s3.utility": Dummy})
        self.config.registry.settings.update(self.S3_Setting)
        self.config.include("altaircms.install_upload_file")
        self.config.add_subscriber(assert_action, "altaircms.filelib.s3.AfterS3Upload")        


        session = self.get_filesession()
        session.add(("test-file", "test-data"),)
        session.commit(extra_args=_result)

    def test_after_s3upload_event_sync_fileurl(self):
        self.config.include("altaircms.asset.install_s3sync")
        from altaircms.filelib.s3 import AfterS3Upload
        session = self.get_filesession().session #wrapped object.
        class uploader:
            bucket_name = ":bucket:"
        files = [File(name=":test-file.jpg:")]
        assets = [DummyAsset(filepath=":test-file.jpg:")]

        self.assertEqual(assets[0].file_url, None)
        self.config.registry.notify(AfterS3Upload(request=None, session=session, files=files, uploader=uploader, extra_args=assets))
        self.assertEqual(assets[0].file_url, "s3://:bucket:/:test-file.jpg:")

    ## delete
    def test_event_is_notified_after_s3delete_with_s3utility(self):
        from altaircms.filelib.s3 import S3ConnectionFactory

        class Dummy(S3ConnectionFactory):
            def delete(self, f, realpath, options=None):
                pass

        _result = object()
        _called = [False]
        matcher = self
        def assert_action(event):
            matcher.assertEquals(event.extra_args, _result)
            _called[0] = True

        self.config.registry.settings.update({"altaircms.s3.utility": Dummy})
        self.config.registry.settings.update(self.S3_Setting)
        self.config.include("altaircms.install_upload_file")
        self.config.add_subscriber(assert_action, "altaircms.filelib.s3.AfterS3Delete")        

        session = self.get_filesession()
        session.delete(("test-file", "test-data"),)
        session.commit(extra_args=_result)

    def test_after_s3delete_event_unpublish_files(self):
        self.config.include("altaircms.asset.install_s3sync")
        from altaircms.filelib.s3 import AfterS3Delete
        session = self.get_filesession().session #wrapped object.
        class uploader:
            bucket_name = ":bucket:"
        files = [File(name=":test-file.jpg:")]
        assets = [DummyAsset(filepath=":test-file.jpg:")]

        self.assertEqual(assets[0].called_all_files_candidates, False)
        self.config.registry.notify(AfterS3Delete(request=None, session=session, files=files, uploader=uploader, extra_args=assets))
        self.assertEqual(assets[0].called_all_files_candidates, True)

if __name__ == "__main__":
    unittest.main()
