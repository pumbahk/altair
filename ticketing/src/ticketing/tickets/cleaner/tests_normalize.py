# -*- coding:utf-8 -*-
import unittest
import os.path
from ticketing.tickets.cleaner.normalize import LBrace, RBrace, Content

class EventsFromStringTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from ticketing.tickets.cleaner.normalize import tokens_from_string
        return tokens_from_string(*args, **kwargs)

    def test_token_from_string__simple(self):
        string = "{}"
        result = self._callFUT(string)
        self.assertEquals(result, [LBrace("{"), RBrace("}")])

    def test_token_from_string__simple_with_dusty_input(self):
        string = "xx{yyy}zzz"
        result = self._callFUT(string)
        self.assertEquals(result, [Content("xx"), LBrace("{"),Content("yyy"), RBrace("}"), Content("zzz")])

    def test_token_from_string__complex(self):
        string = "{{}{}}"
        result = self._callFUT(string)
        self.assertEquals(result, [LBrace("{"), LBrace("{"), RBrace("}"), LBrace("{"), RBrace("}"), RBrace("}")])

    def test_token_from_string__complex_with_dusty_input(self):
        string = "@@@{bbb{cc}dd{}e}"
        result = self._callFUT(string)
        self.assertEquals(result, [Content("@@@"), LBrace("{"), Content("bbb"), LBrace("{"), Content("cc"), RBrace("}"), Content("dd"), LBrace("{"), RBrace("}"), Content("e"), RBrace("}")])


class SVGNormalizeUnitTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from ticketing.tickets.cleaner.normalize import _normalize
        return _normalize(*args, **kwargs)

    def test_it(self):
        from StringIO import StringIO
        io = StringIO(u"""<doc>{{<flowSpan style="font-weight:bold">価格}}</flowSpan></doc>""".encode("utf-8"))

        result = StringIO()
        self._callFUT(io, result)
        self.assertEquals(u'<doc><flowSpan style="font-weight:bold">{{価格}}</flowSpan></doc>', result.getvalue().decode("utf-8"))


    def test_cleaned_xml0(self):
        """<a>{{bb}}</a> -> <a>{{bb}}</a>"""
        from StringIO import StringIO
        io = StringIO("<a>{{bb}}</a>")

        result = StringIO()
        self._callFUT(io, result)
        self.assertEquals("<a>{{bb}}</a>", result.getvalue())

    def test_cleaned_xml1(self):
        """<a>{{bb}} {{cc}}</a> -> <a>{{bb}} {{cc}}</a>"""
        from StringIO import StringIO
        io = StringIO("<a>{{bb}} {{c}}</a>")

        result = StringIO()
        self._callFUT(io, result)
        self.assertEquals("<a>{{bb}} {{c}}</a>", result.getvalue())

    def test_cleaned_xml2(self):
        """<a>{{bb</a>}} -> <a>{{bb}}</a>"""
        from StringIO import StringIO
        io = StringIO("<doc><a>{{bb</a>}}</doc>")

        result = StringIO()
        self._callFUT(io, result)
        self.assertEquals("<doc><a>{{bb}}</a></doc>", result.getvalue())

    def test_cleaned_xml3(self):
        """<a>{<b>{ff</b></a>}} -> <a><b>{{ff}}</b></a>"""
        from StringIO import StringIO
        io = StringIO("<doc><a>{<b>{ff</b></a>}}</doc>")

        result = StringIO()
        self._callFUT(io, result)
        self.assertEquals("<doc><a><b>{{ff}}</b></a></doc>", result.getvalue())

    def test_cleaned_xml4(self):
        """<a>{<b>{ff}}</b></a> -> <a><b>{{ff}}</b></a>"""
        from StringIO import StringIO
        io = StringIO("<doc><a>{<b>{ff}}</b></a></doc>")

        result = StringIO()
        self._callFUT(io, result)
        self.assertEquals("<doc><a><b>{{ff}}</b></a></doc>", result.getvalue())

    def test_cleaned_xml5(self):
        """<a>{</a>{ff}<b>}</b> -> <a></a>{{ff}}<b></b>"""
        from StringIO import StringIO
        io = StringIO("<doc><a>{</a>{ff}<b>}</b></doc>")

        result = StringIO()
        self._callFUT(io, result)
        self.assertEquals('<doc><a></a>{{ff}}<b></b></doc>', result.getvalue())

    def test_cleaned_xml6(self):
        """<a>{{hhh}} --- {{ii}</a>} -> <a>{{hhh}} --- {{ii}}</a>"""
        from StringIO import StringIO
        io = StringIO("<doc><a>{{hhh}} --- {{ii}</a>}</doc>")

        result = StringIO()
        self._callFUT(io, result)
        self.assertEquals("<doc><a>{{hhh}} --- {{ii}}</a></doc>", result.getvalue())

    def test_cleaned_xml7(self):
        """<a>{{hhh}} --- {</a>{ii}} -> <a>{{hhh}} --- </a>{{ii}}"""
        from StringIO import StringIO
        io = StringIO("<doc><a>{{hhh}} --- {</a>{ii}}</doc>")

        result = StringIO()
        self._callFUT(io, result)
        self.assertEquals("<doc><a>{{hhh}} --- </a>{{ii}}</doc>", result.getvalue())

    def test_cleaned_xml8(self):
        """<a><b> xxx </b> {{</a>yyy}}"""
        from StringIO import StringIO
        io = StringIO("<doc><a><b> xxx </b> {{</a>yyy}}</doc>")

        result = StringIO()
        self._callFUT(io, result)
        self.assertEquals("<doc><a><b> xxx </b> </a>{{yyy}}</doc>", result.getvalue())

    def test_cleaned_xml9(self):
        """<a><b> xxx </b> {{y</a>yy}}"""
        from StringIO import StringIO
        io = StringIO("<doc><a><b> xxx </b> {{y</a>yy}}</doc>")

        result = StringIO()
        self._callFUT(io, result)
        self.assertEquals("<doc><a><b> xxx </b> {{yyy}}</a></doc>", result.getvalue())

    def test_cleaned_xml10(self):
        """<a><b> xxx </b> {{y</a>yy}}"""
        from StringIO import StringIO
        io = StringIO("<doc><a><b> x{x}x </b> {{y</a>yy}}</doc>")
        
        result = StringIO()
        self._callFUT(io, result)
        self.assertEquals("<doc><a><b> x{x}x </b> {{yyy}}</a></doc>", result.getvalue())

        
class EliminatedTagNormalizeUnitTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from ticketing.tickets.cleaner.normalize import _normalize
        return _normalize(*args, **kwargs)

    def test_it(self):
        """<F id=1>{{<F id=2>zz</F><f id=3>}}</F></F> -> <F id=1>{{zz}}</F>"""
        from StringIO import StringIO
        io = StringIO('<F id="1">{{<F id="2">zz</F><F id="3">}}</F></F>')

        result = StringIO()
        self._callFUT(io, result, eliminate=True)
        self.assertEquals('<F id="1">{{zz}}</F>', result.getvalue())

    def test_it2(self):
        """<F id=1>{{<F id=2>zz</F><f id=3>}}</F></F> -> <F id=1>{{zz}}</F>"""
        from StringIO import StringIO
        io = StringIO('<doc>{{<F id="2">zz</F><F id="3">}}</F></doc>')

        result = StringIO()
        self._callFUT(io, result, eliminate=True)
        self.assertEquals('<doc><F id="2">{{zz}}</F></doc>', result.getvalue())

    def test_complex(self):
        """ そのまま{{}}の中の文字列をmustacheで文字列を埋め込もうとするとxmlとして不正な形式になり失敗する.normalizeした後のものはok
        """
        from StringIO import StringIO
        import pystache
        import lxml.etree
        svg_file = os.path.join(os.path.dirname(__file__), "sample.svg")

        ## occur xml syntax error using non normalized svg 
        render = pystache.Renderer()
        emitted = render.render(open(svg_file).read().decode("utf-8"), {u"name": "--name--"})
        io = StringIO()
        io.write(emitted.encode("utf-8"))
        io.seek(0)

        with self.assertRaises(lxml.etree.XMLSyntaxError):
            lxml.etree.parse(io)

        ## normalized svg
        io = StringIO()
        with open(svg_file) as rf:
            self._callFUT(rf, io, eliminate=True)            

        render = pystache.Renderer()
        emitted = render.render(io.getvalue().decode("utf-8"), {u"名前": "--name--"})
        io = StringIO()
        io.write(emitted.encode("utf-8"))
        io.seek(0)
        
        self.assertTrue(lxml.etree.parse(io))


class RegressionTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from ticketing.tickets.cleaner.normalize import _normalize
        return _normalize(*args, **kwargs)

    data = u"""\
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:cc="http://creativecommons.org/ns#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   sodipodi:docname="マンシング.svg"
   inkscape:version="0.48.4 r9939"
   height="269.29132"
   width="630.70862"
   version="1.2"
   inkscape:label="Layer"
   id="svg2">
  <metadata
     id="metadata58">
    <rdf:RDF>
      <cc:Work
         rdf:about="">
        <dc:format>image/svg+xml</dc:format>
        <dc:type
           rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
        <dc:title></dc:title>
      </cc:Work>
    </rdf:RDF>
  </metadata>
  <defs
     id="defs56">
    <inkscape:perspective
       sodipodi:type="inkscape:persp3d"
       inkscape:persp3d-origin="315.28345 : 76.818893 : 1"
       inkscape:vp_z="630.56689 : 115.22834 : 1"
       inkscape:vp_x="0 : 115.22834 : 1"
       inkscape:vp_y="0 : 1000 : 0"
       id="perspective3022" />
    <clipPath
       id="clipPath16">
      <path
         d="M 7,7 571,7 571,835 7,835 7,7 z"
         inkscape:connector-curvature="0"
         id="path18" />
    </clipPath>
    <clipPath
       clipPathUnits="userSpaceOnUse"
       id="clipPath3018">
      <path
         id="path3020"
         d="M 0,300 300,300 300,0 0,0 0,300 z"
         inkscape:connector-curvature="0" />
    </clipPath>
    <clipPath
       id="clipPath16-9">
      <path
         d="M 7,7 571,7 571,835 7,835 7,7 z"
         inkscape:connector-curvature="0"
         id="path18-7" />
    </clipPath>
  </defs>
  <sodipodi:namedview
     inkscape:zoom="1"
     borderopacity="1"
     inkscape:current-layer="layer8"
     inkscape:cx="439.82672"
     inkscape:window-y="-8"
     inkscape:snap-grids="false"
     id="namedview54"
     inkscape:window-maximized="1"
     showgrid="false"
     inkscape:guide-bbox="true"
     units="mm"
     showguides="true"
     bordercolor="#666666"
     inkscape:window-x="-8"
     guidetolerance="10"
     objecttolerance="10"
     inkscape:cy="75.72386"
     inkscape:window-width="1600"
     inkscape:pageopacity="0"
     inkscape:pageshadow="2"
     pagecolor="#ffffff"
     gridtolerance="10"
     inkscape:snap-to-guides="false"
     inkscape:document-units="mm"
     inkscape:window-height="838">
    <sodipodi:guide
       position="63.993164,175.71604"
       orientation="1,0"
       id="guide3037" />
    <sodipodi:guide
       position="496.99999,160.5"
       orientation="1,0"
       id="guide3149" />
    <sodipodi:guide
       position="0,0"
       orientation="0,628.93701"
       id="guide3121" />
    <sodipodi:guide
       position="631.24998,0.74999998"
       orientation="-230.31496,0"
       id="guide3123" />
    <sodipodi:guide
       position="10.253048,269.40768"
       orientation="0,-628.93701"
       id="guide3125" />
    <sodipodi:guide
       position="0,230.31496"
       orientation="230.31496,0"
       id="guide3127" />
    <sodipodi:guide
       position="70.710676,226.98127"
       orientation="1,0"
       id="guide3541" />
    <sodipodi:guide
       position="209.65716,262.33661"
       orientation="0,1"
       id="guide3607" />
    <sodipodi:guide
       position="247.99999,196.99999"
       orientation="0,1"
       id="guide3609" />
    <sodipodi:guide
       position="503.24999,96.499998"
       orientation="1,0"
       id="guide3098" />
    <sodipodi:guide
       position="224,29"
       orientation="0,1"
       id="guide3223" />
    <sodipodi:guide
       position="488.99999,159"
       orientation="1,0"
       id="guide3225" />
    <sodipodi:guide
       position="7.0710676,230.87036"
       orientation="1,0"
       id="guide3230" />
  </sodipodi:namedview>
  <g
     sodipodi:insensitive="true"
     style="display:inline"
     inkscape:label="Layer"
     id="layer7"
     inkscape:groupmode="layer" />
  <g
     style="display:inline"
     inkscape:label="Layer#1"
     id="layer8"
     inkscape:groupmode="layer">
    <flowRoot
       style="font-size: 10px; font-style: normal; font-variant: normal; font-weight: 900; font-stretch: normal; line-height: 125%; letter-spacing: 0; word-spacing: 0; writing-mode: lr-tb; text-anchor: middle; fill: #000; fill-opacity: 1; stroke: none; display: inline; font-family: MS PGothic; -inkscape-font-specification: MS PGothic"
       xml:space="preserve"
       id="flowRoot3020"><flowRegion
         id="flowRegion29"><rect
           style="fill:none; stroke:none;"
           height="30.0"
           width="437.0"
           stroke="none"
           y="92.766409"
           x="159.029613"
           id="rect3024"
           fill="none" /></flowRegion><flowDiv
         id="flowDiv32"><flowPara
           id="flowPara34" /></flowDiv></flowRoot>    <flowRoot
       style="font-size: 10px; font-style: normal; font-variant: normal; font-weight: bold; font-stretch: normal; text-align: start; line-height: 125%; letter-spacing: 0; word-spacing: 0; writing-mode: lr-tb; text-anchor: start; fill: #000; fill-opacity: 1; stroke: none; display: inline; font-family: MS PGothic; -inkscape-font-specification: MS PGothic Bold"
       xml:space="preserve"
       id="flowRoot3056-4"><flowRegion
         id="flowRegion37"><rect
           style="fill:none; stroke:none;"
           height="26.0"
           width="405.55554"
           stroke="none"
           y="177.312827"
           x="73.6332486"
           id="rect3060-8"
           fill="none" /></flowRegion><flowDiv
         style="text-align: start; line-height: 100%; text-anchor: start"
         id="flowDiv40"><flowPara
           style="font-size: 10px"
           id="flowPara42" /><flowPara
           style="font-size: 20px"
           id="flowPara44" /></flowDiv></flowRoot>    <flowRoot
       style="font-size: 10px; font-style: normal; font-variant: normal; font-weight: bold; font-stretch: normal; text-align: start; line-height: 125%; letter-spacing: 0; word-spacing: 0; writing-mode: lr-tb; text-anchor: start; fill: #000; fill-opacity: 1; stroke: none; display: inline; font-family: MS PGothic; -inkscape-font-specification: MS PGothic Bold"
       xml:space="preserve"
       id="flowRoot3250-8"><flowRegion
         id="flowRegion47"><rect
           style="fill:none; stroke:none;"
           height="12.277779"
           width="227.22223"
           stroke="none"
           y="100.624662"
           x="73.4441545"
           id="rect3254-6"
           fill="none" /></flowRegion><flowDiv
         style="font-size: 10px; line-height: 100%"
         id="flowDiv50"><flowPara
           id="flowPara52" /></flowDiv></flowRoot>    <flowRoot
       style="font-size:10px;font-style:normal;font-variant:normal;font-weight:bold;font-stretch:normal;text-align:start;line-height:125%;letter-spacing:0;word-spacing:0;writing-mode:lr-tb;text-anchor:start;fill:#000000;fill-opacity:1;stroke:none;display:inline;font-family:MS PGothic;-inkscape-font-specification:MS PGothic Bold"
       xml:space="preserve"
       id="flowRoot3250-5"
       transform="translate(26,-22)"><flowRegion
         id="flowRegion63"><rect
           style="fill:none;stroke:none"
           height="13.166672"
           width="354.14182"
           y="242.79861"
           x="73.408997"
           id="rect3254-38" /></flowRegion><flowDiv
         style="font-size:9px"
         id="flowDiv66"><flowPara
           id="flowPara68">予約番号：{{予約番号}}</flowPara></flowDiv></flowRoot>    <flowRoot
       style="font-size: 10px; font-style: normal; font-variant: normal; font-weight: bold; font-stretch: normal; text-align: start; line-height: 125%; letter-spacing: 0; word-spacing: 0; writing-mode: lr-tb; text-anchor: start; fill: #000; fill-opacity: 1; stroke: none; display: inline; font-family: MS PGothic; -inkscape-font-specification: MS PGothic Bold"
       xml:space="preserve"
       id="flowRoot3056-2-9"><flowRegion
         id="flowRegion71"><rect
           style="fill:none; stroke:none;"
           height="23.0"
           width="116.38889"
           stroke="none"
           y="117.5996919"
           x="381.821955"
           id="rect3060-6-1"
           fill="none" /></flowRegion><flowDiv
         style="font-size: 12px; line-height: 100%"
         id="flowDiv74"><flowPara
           id="flowPara76" /></flowDiv></flowRoot>    <flowRoot
       style="font-size: 12px; font-style: normal; font-variant: normal; font-weight: bold; font-stretch: normal; text-align: start; line-height: 125%; letter-spacing: 0; word-spacing: 0; writing-mode: lr-tb; text-anchor: start; fill: #000; fill-opacity: 1; stroke: none; display: inline; font-family: MS PGothic; -inkscape-font-specification: MS PGothic Bold"
       xml:space="preserve"
       id="flowRoot3056-2-9-0"><flowRegion
         id="flowRegion79"><rect
           style="fill:none; stroke:none;"
           height="13.166661"
           width="126.65061"
           stroke="none"
           y="189.694453"
           x="170.512264"
           id="rect3060-6-1-0"
           fill="none" /></flowRegion><flowDiv
         style="font-size: 12px; text-align: start; line-height: 100%; text-anchor: start"
         id="flowDiv82"><flowPara
           id="flowPara84" /></flowDiv></flowRoot>    <flowRoot
       style="font-size: 10px; font-style: normal; font-variant: normal; font-weight: bold; font-stretch: normal; text-align: start; line-height: 125%; letter-spacing: 0; word-spacing: 0; writing-mode: lr-tb; text-anchor: start; fill: #000; fill-opacity: 1; stroke: none; display: inline; font-family: MS PGothic; -inkscape-font-specification: MS PGothic Bold"
       xml:space="preserve"
       id="flowRoot3250-0"><flowRegion
         id="flowRegion99"><rect
           style="fill:none; stroke:none;"
           ry="0"
           height="16.499989"
           width="376.24707"
           stroke="none"
           y="187.798621"
           x="73.9349385"
           id="rect3254-37"
           fill="none" /></flowRegion><flowDiv
         style="font-size: 14px"
         id="flowDiv102"><flowPara
           style="line-height: 100%"
           id="flowPara104" /><flowPara
           id="flowPara106" /></flowDiv></flowRoot>    <flowRoot
       style="font-size: 10px; font-style: normal; font-variant: normal; font-weight: 900; font-stretch: normal; line-height: 125%; letter-spacing: 0; word-spacing: 0; writing-mode: lr-tb; text-anchor: middle; fill: #000; fill-opacity: 1; stroke: none; display: inline; font-family: MS PGothic; -inkscape-font-specification: MS PGothic"
       xml:space="preserve"
       id="flowRoot3020-1"><flowRegion
         id="flowRegion109"><rect
           style="fill:none; stroke:none;"
           height="30.0"
           width="437.0"
           stroke="none"
           y="92.766409"
           x="159.029613"
           id="rect3024-4"
           fill="none" /></flowRegion><flowDiv
         id="flowDiv112"><flowPara
           id="flowPara114" /></flowDiv></flowRoot>    <flowRoot
       style="font-size: 10px; font-style: normal; font-variant: normal; font-weight: 900; font-stretch: normal; line-height: 125%; letter-spacing: 0; word-spacing: 0; writing-mode: lr-tb; text-anchor: middle; fill: #000; fill-opacity: 1; stroke: none; display: inline; font-family: MS PGothic; -inkscape-font-specification: MS PGothic"
       xml:space="preserve"
       id="flowRoot3020-2"><flowRegion
         id="flowRegion117"><rect
           style="fill:none; stroke:none;"
           height="30.0"
           width="437.0"
           stroke="none"
           y="92.766409"
           x="159.029613"
           id="rect3024-2"
           fill="none" /></flowRegion><flowDiv
         id="flowDiv120"><flowPara
           id="flowPara122" /></flowDiv></flowRoot>    <flowRoot
       style="font-size:8px;font-style:normal;font-variant:normal;font-weight:bold;font-stretch:normal;text-align:start;line-height:125%;letter-spacing:0;word-spacing:0;writing-mode:lr-tb;text-anchor:start;fill:#000000;fill-opacity:1;stroke:none;display:inline;font-family:MS PGothic;-inkscape-font-specification:MS PGothic Bold"
       xml:space="preserve"
       id="flowRoot3056-2-42"
       transform="translate(-6,-16)"><flowRegion
         id="flowRegion125"><rect
           style="font-size:8px;fill:none;stroke:none"
           height="190.27776"
           width="122.38889"
           y="51.515617"
           x="505.53552"
           id="rect3060-6-7" /></flowRegion><flowDiv
         style="font-size:8px;line-height:100%"
         id="flowDiv128"><flowPara
           id="flowPara130" /><flowPara
           id="flowPara3169">第44回</flowPara><flowPara
           id="flowPara3173">マンシングウェアレディース</flowPara><flowPara
           id="flowPara3175">東海クラシック </flowPara><flowPara
           id="flowPara134" /><flowPara
           id="flowPara162" /><flowPara
           id="flowPara164" /></flowDiv></flowRoot>    <flowRoot
       style="font-size:10px;font-style:normal;font-variant:normal;font-weight:bold;font-stretch:normal;text-align:start;line-height:125%;letter-spacing:0;word-spacing:0;writing-mode:lr-tb;text-anchor:start;fill:#000000;fill-opacity:1;stroke:none;display:inline;font-family:MS PGothic;-inkscape-font-specification:MS PGothic Bold"
       xml:space="preserve"
       id="flowRoot3056-2-42-5"><flowRegion
         id="flowRegion167"><rect
           style="fill:none;stroke:none"
           height="162.36739"
           width="55.193401"
           y="101.08879"
           x="3.937295"
           id="rect3060-6-7-2" /></flowRegion><flowDiv
         style="line-height:100%"
         id="flowDiv170"><flowPara
           style="font-size:8px"
           id="flowPara172">{{</flowPara><flowPara
           style="font-size:6px"
           id="flowPara174" /><flowPara
           style="font-size:6px"
           id="flowPara176">{{券種名}}</flowPara><flowPara
           style="font-size:6px"
           id="flowPara180" /><flowPara
           style="font-size:6px"
           id="flowPara182" /><flowPara
           style="font-size:6px"
           id="flowPara184">{{チケット価格}}</flowPara><flowPara
           style="font-size:6px"
           id="flowPara186" /><flowPara
           style="font-size:6px"
           id="flowPara188">{{予約番号}}</flowPara><flowPara
           style="font-size:8px"
           id="flowPara190" /><flowPara
           style="font-size:8px"
           id="flowPara192" /></flowDiv></flowRoot>    <flowRoot
       style="font-size: 10px; font-style: normal; font-variant: normal; font-weight: bold; font-stretch: normal; text-align: start; line-height: 125%; letter-spacing: 0; word-spacing: 0; writing-mode: lr-tb; text-anchor: start; fill: #000; fill-opacity: 1; stroke: none; display: inline; font-family: MS PGothic; -inkscape-font-specification: MS PGothic Bold"
       xml:space="preserve"
       id="flowRoot3250-3-9-7"><flowRegion
         id="flowRegion195"><rect
           style="fill:none; stroke:none;"
           height="10.944443"
           width="62.800003"
           stroke="none"
           y="243.505673"
           x="10.0"
           id="rect3254-3-5-9"
           fill="none" /></flowRegion><flowDiv
         style="font-size: 6px"
         id="flowDiv198"><flowPara
           id="flowPara200" /><flowPara
           id="flowPara202" /></flowDiv></flowRoot>    <flowRoot
       style="font-size: 10px; font-style: normal; font-variant: normal; font-weight: bold; font-stretch: normal; text-align: start; line-height: 125%; letter-spacing: 0; word-spacing: 0; writing-mode: lr-tb; text-anchor: start; fill: #000; fill-opacity: 1; stroke: none; display: inline; font-family: MS PGothic; -inkscape-font-specification: MS PGothic Bold"
       xml:space="preserve"
       id="flowRoot3250-8-44"><flowRegion
         id="flowRegion205"><rect
           style="fill:none; stroke:none;"
           height="86.411301"
           width="413.80981"
           stroke="none"
           y="78.992126"
           x="73.991028"
           id="rect3254-6-1"
           fill="none" /></flowRegion><flowDiv
         style="font-size: 10px; line-height: 100%"
         id="flowDiv208"><flowPara
           id="flowPara210" /></flowDiv></flowRoot>    <flowRoot
       xml:space="preserve"
       style="font-size:8px;font-style:normal;font-weight:normal;line-height:100%;letter-spacing:0;word-spacing:0;fill:#000000;fill-opacity:1;stroke:none;font-family:MS PGothic;-inkscape-font-specification:MS PMincho"
       id="flowRoot3203"
       transform="translate(15,67)"><flowRegion
         id="flowRegion213"><rect
           style="font-size:8px;font-weight:normal;fill:none;stroke:none;-inkscape-font-specification:MS PMincho"
           height="117"
           width="578"
           y="58.291321"
           x="81"
           id="rect3207" /></flowRegion><flowDiv
         style="font-size:8px;font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;line-height:100%;font-family:MS PGothic;-inkscape-font-specification:MS PMincho"
         id="flowDiv216"><flowPara
           style="font-size:8px;font-weight:normal;-inkscape-font-specification:MS PMincho"
           id="flowPara218" /><flowPara
           style="font-size:8px;font-weight:normal;-inkscape-font-specification:MS PMincho"
           id="flowPara220">■主催：東海テレビ放送、株式会社デサント　　　■競技運営：ダンロップスポーツエンタープライズ　　</flowPara><flowPara
           style="font-size:8px;font-weight:normal;-inkscape-font-specification:MS PMincho"
           id="flowPara222">■協賛：株式会社LIXIL、エプソン販売株式会社</flowPara><flowPara
           style="font-size:8px;font-weight:normal;-inkscape-font-specification:MS PMincho"
           id="flowPara224">■優勝副賞：ブルガリジャパン株式会社</flowPara><flowPara
           style="font-size:8px;font-weight:normal;-inkscape-font-specification:MS PMincho"
           id="flowPara226">■お問合せ：マンシングウェアレディース東海クラシック事務局　052-951-2511(東海テレビ放送代表)</flowPara><flowPara
           style="font-size:8px;font-weight:normal;-inkscape-font-specification:MS PMincho"
           id="flowPara228">＜高校生以下無料＞</flowPara></flowDiv><flowDiv
         style="font-size:8px;font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;line-height:100%;font-family:MS PGothic;-inkscape-font-specification:MS PMincho"
         id="flowDiv3155" /></flowRoot>    <flowRoot
       xml:space="preserve"
       style="font-size:14px;font-style:normal;font-weight:normal;line-height:125%;letter-spacing:0;word-spacing:0;fill:#000000;fill-opacity:1;stroke:none;font-family:MS PGothic"
       id="flowRoot3233"
       transform="translate(0,-32)"><flowRegion
         id="flowRegion239"><rect
           style="fill:none;stroke:none"
           height="27"
           width="94"
           y="241.29132"
           x="506"
           id="rect3237" /></flowRegion><flowDiv
         style="font-size:8px;font-style:normal;font-variant:normal;font-weight:bold;font-stretch:normal;font-family:MS PGothic;-inkscape-font-specification:MS PGothic Bold"
         id="flowDiv242"><flowPara
           id="flowPara244">{{予約番号}}</flowPara></flowDiv></flowRoot>    <flowRoot
       xml:space="preserve"
       id="flowRoot3221"
       style="font-size:16px;font-style:normal;font-variant:normal;font-weight:bold;font-stretch:normal;line-height:100%;letter-spacing:0px;word-spacing:0px;fill:#000000;fill-opacity:1;stroke:none;font-family:MS PGothic;-inkscape-font-specification:MS PGothic Bold"
       transform="translate(1,-260)"><flowRegion
         id="flowRegion3223"><rect
           id="rect3225"
           width="407"
           height="27"
           x="96"
           y="289.29132"
           style="font-size:16px;font-style:normal;font-variant:normal;font-weight:bold;font-stretch:normal;line-height:100%;font-family:MS PGothic;-inkscape-font-specification:MS PGothic Bold" /></flowRegion><flowPara
         id="flowPara3227">第44回マンシングウェアレディース東海クラシック</flowPara></flowRoot>    <flowRoot
       xml:space="preserve"
       id="flowRoot3229"
       style="font-size:12px;font-style:normal;font-variant:normal;font-weight:bold;font-stretch:normal;line-height:100%;letter-spacing:0px;word-spacing:0px;fill:#000000;fill-opacity:1;stroke:none;font-family:MS PGothic;-inkscape-font-specification:MS PGothic Bold"
       transform="translate(-7,-283)"><flowRegion
         id="flowRegion3231"><rect
           id="rect3233"
           width="391"
           height="18"
           x="104"
           y="339.29132"
           style="font-size:12px;font-style:normal;font-variant:normal;font-weight:bold;font-stretch:normal;line-height:100%;font-family:MS PGothic;-inkscape-font-specification:MS PGothic Bold" /></flowRegion><flowPara
         id="flowPara3235">開催期間：2013年　9月20日（金）　予選　8:00AMスタート予定</flowPara></flowRoot>    <flowRoot
       xml:space="preserve"
       id="flowRoot3237"
       style="fill:black;stroke:none;stroke-opacity:1;stroke-width:1px;stroke-linejoin:miter;stroke-linecap:butt;fill-opacity:1;font-family:MS PGothic;font-style:normal;font-weight:bold;font-size:10px;line-height:100%;letter-spacing:0px;word-spacing:0px;-inkscape-font-specification:MS PGothic Bold;font-stretch:normal;font-variant:normal"><flowRegion
         id="flowRegion3239"><rect
           id="rect3241"
           width="315"
           height="29"
           x="107"
           y="367.29132"
           style="-inkscape-font-specification:MS PGothic Bold;font-family:MS PGothic;font-weight:bold;font-style:normal;font-stretch:normal;font-variant:normal;line-height:100%" /></flowRegion><flowPara
         id="flowPara3243" /></flowRoot>    <flowRoot
       xml:space="preserve"
       id="flowRoot3145"
       style="font-size:12px;font-style:normal;font-variant:normal;font-weight:bold;font-stretch:normal;line-height:100%;letter-spacing:0px;word-spacing:0px;fill:#000000;fill-opacity:1;stroke:none;font-family:MS PGothic;-inkscape-font-specification:MS PGothic Bold"
       transform="translate(-72,-200)"><flowRegion
         id="flowRegion3147"><rect
           id="rect3149"
           width="385"
           height="18"
           x="170"
           y="299.29132"
           style="font-size:12px;font-style:normal;font-variant:normal;font-weight:bold;font-stretch:normal;line-height:100%;font-family:MS PGothic;-inkscape-font-specification:MS PGothic Bold" /></flowRegion><flowPara
         id="flowPara3151">開催場所：新南愛知カントリークラブ　美浜コース</flowPara></flowRoot>    <flowRoot
       xml:space="preserve"
       id="flowRoot3157"
       style="font-size:12px;font-style:normal;font-variant:normal;font-weight:bold;font-stretch:normal;line-height:125%;letter-spacing:0px;word-spacing:0px;fill:#000000;fill-opacity:1;stroke:none;font-family:MS PGothic;-inkscape-font-specification:MS PGothic Bold"
       transform="translate(0,8)"><flowRegion
         id="flowRegion3159"><rect
           id="rect3161"
           width="241"
           height="28"
           x="98"
           y="193.29132"
           style="font-size:12px;font-style:normal;font-variant:normal;font-weight:bold;font-stretch:normal;font-family:MS PGothic;-inkscape-font-specification:MS PGothic Bold" /></flowRegion><flowPara
         id="flowPara3163">{{券種名}}　　　{{チケット価格}}(税込)</flowPara></flowRoot>    <flowRoot
       xml:space="preserve"
       id="flowRoot3132"
       style="font-size:10px;font-style:normal;font-variant:normal;font-weight:bold;font-stretch:normal;line-height:100%;letter-spacing:0px;word-spacing:0px;fill:#000000;fill-opacity:1;stroke:none;font-family:MS PGothic;-inkscape-font-specification:MS PGothic Bold"
       transform="translate(-6,34)"><flowRegion
         id="flowRegion3134"><rect
           id="rect3136"
           width="113"
           height="43"
           x="508"
           y="103.29132"
           style="font-style:normal;font-variant:normal;font-weight:bold;font-stretch:normal;line-height:100%;font-family:MS PGothic;-inkscape-font-specification:MS PGothic Bold" /></flowRegion><flowPara
         id="flowPara3138">{{券種名}}</flowPara><flowPara
         id="flowPara3140">{{チケット価格}}(税込)</flowPara></flowRoot>    <flowRoot
       xml:space="preserve"
       id="flowRoot3138"
       style="font-size:8px;font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;line-height:100%;letter-spacing:0px;word-spacing:0px;fill:#000000;fill-opacity:1;stroke:none;font-family:MS PGothic;-inkscape-font-specification:MS PGothic"
       transform="translate(-2,-68)"><flowRegion
         id="flowRegion3140"><rect
           id="rect3142"
           width="354"
           height="63"
           x="101"
           y="243.29132"
           style="font-size:8px;font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;line-height:100%;font-family:MS PGothic;-inkscape-font-specification:MS PGothic" /></flowRegion><flowPara
         id="flowPara3144">※本券は引換券となります。</flowPara><flowPara
         id="flowPara3146">　当日、会場にて各日共通3枚綴りとお引換えください。</flowPara></flowRoot>    <flowRoot
       xml:space="preserve"
       id="flowRoot3133"
       style="font-size:12px;font-style:normal;font-variant:normal;font-weight:bold;font-stretch:normal;line-height:100%;letter-spacing:0px;word-spacing:0px;fill:#000000;fill-opacity:1;stroke:none;font-family:MS PGothic;-inkscape-font-specification:MS PGothic Bold"
       transform="translate(93,-175)"><flowRegion
         id="flowRegion3135"><rect
           id="rect3137"
           width="354"
           height="69"
           x="119"
           y="242.29132"
           style="font-size:12px;font-style:normal;font-variant:normal;font-weight:bold;font-stretch:normal;line-height:100%;font-family:MS PGothic;-inkscape-font-specification:MS PGothic Bold" /></flowRegion><flowPara
         id="flowPara3139">9月21日（土）　予選　7:30AMスタート予定</flowPara><flowPara
         id="flowPara3141">9月22日（日）　決勝　7:30AMスタート予定</flowPara></flowRoot>  </g>
</svg>
""".encode("utf-8")
    def test_2514(self):
        from StringIO import StringIO
        import pystache
        import lxml.etree
        io = StringIO()
        rf = StringIO(self.data)
        self._callFUT(rf, io, eliminate=True)            

        render = pystache.Renderer()
        emitted = render.render(io.getvalue().decode("utf-8"), {u"名前": "--name--"})
        io = StringIO()
        io.write(emitted.encode("utf-8"))
        io.seek(0)
        
        self.assertTrue(lxml.etree.parse(io))

if __name__ == "__main__":
    unittest.main()
