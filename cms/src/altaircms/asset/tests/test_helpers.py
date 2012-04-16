import unittest
import mock
from altaircms.asset import helpers as h

import contextlib
import os
here = os.path.abspath(os.path.dirname(__file__))

## dummy module os.path .etc
#
class DummyOS(object):
    def __init__(self, cwd):
        self.D = {}
        self.D[cwd] = True
        
        self._output = []

    def remove(self, path):
        self._output.append(("removed", path))

    @contextlib.contextmanager
    def open(self, path, flag): ##w+b
        if "w" in flag:
            import StringIO
            io = StringIO.StringIO()
            self.D[path] = io
            self._output.append((path, io))
            yield io
        else:
            raise Exception("not support")
            
class DummyPath(object):
    def __init__(self, parent):
        self.os = parent

    def join(self, *args):
        return os.path.join(*args)

    def dirname(self, *args):
        return os.path.dirname(*args)

    def exists(self, path):
        return path in self.os.D

def dummy_os(cwd):
    dos = DummyOS(cwd)
    dos.path = DummyPath(dos)
    return dos

class helperTests(unittest.TestCase):
    def test_divide_data(self):
        params = {"foo": None, "tags": "foo, bar", "private_tags": "private"}
        result = h.divide_data(params)
        
        tags, private_tags, params = result
        self.assertEquals(tags, ["foo", "bar"])
        self.assertEquals(private_tags, ["private"])
        self.assertEquals(params, {"foo": None})

    def test_divide_data_no_tagdata(self):
        params = {"foo": None}
        result = h.divide_data(params)
        
        tags, private_tags, params = result
        self.assertEquals(tags, [])
        self.assertEquals(private_tags, [])
        self.assertEquals(params, {"foo": None})

    def test_get_form_params_from_asset(self):
        from altaircms.asset.models import ImageAsset
        asset = ImageAsset(alt="alt", filepath="foo.jpg")
        result = h.get_form_params_from_asset(asset)

        self.assertEquals(result["discriminator"], "image")
        self.assertEquals(result["filepath"], "foo.jpg")
        self.assertEquals(result["alt"], "alt")


    @mock.patch("altaircms.asset.helpers.os")
    def test_delete_file_if_exist(self, mocked_os):
        dos = dummy_os(".")
        dos.D["./foo.py"] = "file-is-exist"
        mocked_os.remove = dos.remove
        mocked_os.path = dos.path
        
        h.delete_file_if_exist("./foo.py")
        result = dos._output.pop()
        self.assertEquals(result, ("removed", "./foo.py"))

    @mock.patch("altaircms.asset.helpers.os")
    def test_delete_file_if_does_not_exist(self, mocked_os):
        dos = dummy_os(".")
        mocked_os.remove = dos.remove
        mocked_os.path = dos.path
        
        h.delete_file_if_exist("./foo.py")
        result = dos._output
        self.assertEquals(result, [])
        
    def test_write_name(self):
        from datetime import date
        filename = "foo.txt"
        uuid_val = "5eff04a4-c3c0-4fce-acc1-5ff3677049ee"

        result = h.get_writename(filename, 
                                 gensym=lambda : uuid_val, 
                                 gendate=lambda : date(2012, 1, 1))
        self.assertEquals(result, "2012-01-01/5eff04a4-c3c0-4fce-acc1-5ff3677049ee.txt")

    @mock.patch("altaircms.asset.helpers.os")
    def testwrite_buf(self, mocked_os):
        dos = dummy_os(".")
        mocked_os.path = dos.path


        h.write_buf("/a/b/c", "e/d.txt", "content value", _open=dos.open)

        result = dos._output.pop()
        saved_path, output = result

        self.assertEquals(saved_path, "/a/b/c/e/d.txt")
        self.assertTrue(mocked_os.makedirs.called)
        self.assertEquals(output.getvalue(), "content value")

    def test_detect_mimetype(self):
        result = h.detect_mimetype("foo/bar/boo.jpg")
        self.assertEquals(result, "image/jpeg")

    def test_detect_mimetype_invalid(self):
        result = h.detect_mimetype("foo/bar/boo.foo")
        self.assertEquals(result,'application/octet-stream')

    ## asset width height
    def test_get_image_status_extra(self):
        with open(os.path.join(here, "test.jpg")) as io:
            result = h.get_image_status_extra(None, io)
            self.assertEquals(result, {'width': 1024, 'height': 685})

    def test_get_movie_status_extra(self):
        result = h.get_movie_status_extra(None, None)
        self.assertEquals(result, {'width': None, 'height': None})

    def test_get_flash_status_extra(self):
        with open(os.path.join(here, "w480h445.compressed.swf")) as io:
            result = h.get_flash_status_extra(None, io)
            self.assertEquals(result, {'width': 480, 'height': 445})


    def test_swf_width_height_compressed(self):
        from altaircms.asset.swfrect import swf_width_and_height
        with open(os.path.join(here, "w480h445.compressed.swf")) as io:
            result = swf_width_and_height(io)

            self.assertEquals(result, (480, 445))

    def test_swf_width_height(self):
        from altaircms.asset.swfrect import swf_width_and_height
        with open(os.path.join(here, "w480h445.swf")) as io:
            result = swf_width_and_height(io)

            self.assertEquals(result, (480, 445))


    def test_swf_width_height_invalid(self):
        from altaircms.asset.swfrect import swf_width_and_height
        with open(__file__) as io:
            self.assertRaises(Exception, lambda : swf_width_and_height(io))
