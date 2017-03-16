# encoding: utf-8

import unittest
import json
from datetime import datetime

class MailerTest(unittest.TestCase):
    def test_it(self):
        from .mu import Mailer, Recipient
        m = Mailer("test@example.org", u"さしだしにん")

        start_time = datetime.strptime("2017/1/2 3:45:06", "%Y/%m/%d %H:%M:%S")
        config_json = m.create_config(start_time, u"さぶじぇくと")
        config = json.loads(config_json)
        self.assertEqual(config["SendStartTime"], "2017-01-02 03:45:06")

        m.set_attributes([ "keywords" ])

        self.assertEqual(m.create_template("abc"), "abc")

        self.assertEqual(m.create_template("abc @@name@@"), "abc ###_NAME_###")

        self.assertEqual(m.create_template("abc @@name@@ xxx @@keywords@@ yyy"), "abc ###_NAME_### xxx ###_ATTRIBUTE1_### yyy")

        self.assertEqual(m.create_template("abc @@hoge@@"), "abc @@hoge@@")

        self.assertEqual(m.create_template(u"あいう @@hoge@@"), u"あいう @@hoge@@")

        r1 = Recipient("https://open_id/123", { "keywords": u"あい, うえ" })
        list1 = m.create_list([ r1 ])
        self.assertEqual(list1, u"https://open_id/123_M#8_M#8_M#8あい, うえ_M#8\n")

        r2 = Recipient("https://open_id/123", { "keywords": u"あい, うえ" })
        list2 = m.create_list([ r2 ])
        self.assertEqual(list2, u"https://open_id/123_M#8_M#8_M#8あい, うえ_M#8\n")

    def test_zip(self):
        from .mu import Mailer, Recipient
        m = Mailer("test@example.org", u"さしだしにん")

        m.set_attributes([ "keywords" ])

        start_time = datetime.now()
        r1 = Recipient("https://open_id/123", { "name": u"ゆーざ", "keywords": u"あい, うえ"})
        r2 = Recipient("https://open_id/123", { "keywords": u"あい, うえ"})
        zip_byte = m.pack_as_zip(start_time, u"さぶじぇくと", u"あいう @@keywords@@", [ r1, r2 ])

        import zipfile
        import io
        buf = io.BytesIO(zip_byte)
        zip = zipfile.ZipFile(buf, "r")
        self.assertEqual([ f.filename for f in zip.filelist ], [ "parameter.json", "template_pc_html.html", "recipients.txt" ])
        self.assertEqual(zip.read(zip.filelist[1].filename), u"あいう ###_ATTRIBUTE1_###".encode('utf-8'))
        self.assertEqual(len(zip.read(zip.filelist[2].filename).splitlines()), 2)
