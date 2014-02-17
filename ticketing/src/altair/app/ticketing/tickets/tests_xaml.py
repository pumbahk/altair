# -*- coding:utf-8 -*-
import unittest
class XAMLFromSVGTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from altair.app.ticketing.tickets.xaml import xaml_from_svg
        return xaml_from_svg(*args, **kwargs)

    def test_it(self):
        ##todo: まじめにtest
        svg = """\
<ns0:svg xmlns:ns0="http://www.w3.org/2000/svg" xmlns:ns1="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd" xmlns:ns2="http://www.inkscape.org/namespaces/inkscape" height="265.74802" id="svg2" version="1.2" width="396.85037" ns2:version="0.48.4 r9939">
  <ns0:defs id="defs200"/>
  <ns1:namedview/>
  <ns0:g id="g28" ns2:groupmode="layer" ns2:label="Text">
    <ns0:flowRoot id="flowRoot184-0-0" style="font-size: 8px; font-style: normal; font-variant: normal; font-weight: bold; font-stretch: normal; text-align: start; line-height: 100%; letter-spacing: 0; word-spacing: 0; writing-mode: lr-tb; text-anchor: start; fill: #000; font-family: MS PGothic">
      <ns0:flowRegion>
        <ns0:rect fill="none" height="14.219651" id="rect188-1-1" stroke="none" style="fill:none; stroke:none;" width="85.951256" x="294.60844" y="211.74922"/>
      </ns0:flowRegion>
      <ns0:flowDiv><ns0:flowPara>{{予約番号}}</ns0:flowPara>
      </ns0:flowDiv></ns0:flowRoot>

    <ns0:path d="m 368.03009,184.69201 c 0,0 -0.80702,1.86877 -0.80702,1.86877 0,0 z" id="path3337" style="fill:#231f20;fill-opacity:1;fill-rule:nonzero;stroke:none" ns2:connector-curvature="0"/>
  </ns0:g>
</ns0:svg>"""
        result = self._callFUT(svg, pretty_print=False)
        expected = """\
<FixedDocument xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml" xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"><PageContent><FixedPage Width="396.85037" Height="265.74802"><Canvas><TextBlock TextWrapping="Wrap" Width="85.951256" Height="14.219651" Canvas.Left="294.60844" Canvas.Top="211.74922" FontSize="8px" FontFamily="MS PGothic" Foreground="#000" FontStyle="Normal" FontWeight="Bold">{{予約番号}}</TextBlock><Path Data="m 368.03009,184.69201 c 0,0 -0.80702,1.86877 -0.80702,1.86877 0,0 z" Fill="#231f20" Opacity="1"/></Canvas></FixedPage></PageContent></FixedDocument>"""
        self.assertEqual(expected, result)
