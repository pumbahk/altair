#-*- coding:utf-8 -*-
import unittest

class RegressionTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from altair.app.ticketing.tickets.cleaner.normalize import _normalize
        return _normalize(*args, **kwargs)

    data = u"""\
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
    xmlns:svg="http://www.w3.org/2000/svg"
    version="1.2"
    id="svg2">
  <g>
    <flowRoot id="x">
      <flowDiv id="a">
        <flowPara id="this-is-evil-of-root">{{</flowPara><flowPara style="font-size:6px" id="flowPara176">{{券種名}}</flowPara>
        <flowPara style="font-size:8px" id="flowPara192" />

        <flowPara id="i1"/>
      </flowDiv>
    </flowRoot> 
    <flowRoot id="y">
      <flowRegion id="r0">
        <rect id="r0" />
      </flowRegion>
      <flowDiv id="b">
        <flowPara id="j0" />
        <flowPara id="j1" />
      </flowDiv>
    </flowRoot> 
  </g>
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

    def test_3616(self):
        from StringIO import StringIO
        import pystache
        import lxml.etree
        io = StringIO()
        rf = StringIO(u"<svg><tspan><tspan>text</tspan>)</tspan></svg>")
        self._callFUT(rf, io, eliminate=True)            

        render = pystache.Renderer()
        emitted = render.render(io.getvalue(), {})
        io = StringIO()
        io.write(emitted)
        io.seek(0)
        self.assertTrue(lxml.etree.parse(io))

if __name__ == "__main__":
    unittest.main()
