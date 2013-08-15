from unittest import TestCase

class CP932NormalizedTildeTest(TestCase):
    def testRegisterCodecs(self):
        from . import register_codecs
        import codecs
        import exceptions
        with self.assertRaises(exceptions.LookupError):
            codecs.getencoder('cp932:normalized-tilde')
        register_codecs()
        codecs.getencoder('cp932:normalized-tilde')
        "\x81`".decode('cp932:normalized-tilde')

    def testDecoder(self):
        from .cp932_normalized_tilde import cp932_normalized_tilde
        self.assertEqual(cp932_normalized_tilde.decode('\x81`'), (u"\u301c", 2))

    def testStreamReader(self):
        from .cp932_normalized_tilde import cp932_normalized_tilde
        from cStringIO import StringIO
        x = cp932_normalized_tilde.streamreader(StringIO("\x81`\n\x81`"))
        self.assertEqual(x.readline(), u"\u301c\n")
        self.assertEqual(x.readline(None, False), u"\u301c")

    def testIncrementalDecoder(self):
        from .cp932_normalized_tilde import cp932_normalized_tilde
        dec = cp932_normalized_tilde.incrementaldecoder()
        self.assertEqual(dec.decode("\x81"), u"")
        self.assertEqual(dec.decode("`"), u"\u301c")


