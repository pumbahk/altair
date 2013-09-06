# encoding: utf-8

from unittest import TestCase
from datetime import datetime
from lxml import etree
from mock import Mock

class Regression(TestCase):
    def test_h(self):
        from .convert import EmittingPathDataHandler
        from altair.svg.path import PathDataScanner

        emitter = Mock()
        PathDataScanner(['m', '10', '0', 'h', '10'], EmittingPathDataHandler(emitter))()

        emitter.emit_move_to.assert_called_once_with(10, 0)
        emitter.emit_line_to.assert_called_once_with(20, 0)

    def test_H(self):
        from .convert import EmittingPathDataHandler
        from altair.svg.path import PathDataScanner

        emitter = Mock()
        PathDataScanner(['m', '10', '0', 'H', '20'], EmittingPathDataHandler(emitter))()

        emitter.emit_move_to.assert_called_once_with(10, 0)
        emitter.emit_line_to.assert_called_once_with(20, 0)

    def test_v(self):
        from .convert import EmittingPathDataHandler
        from altair.svg.path import PathDataScanner

        emitter = Mock()
        PathDataScanner(['m', '0', '10', 'v', '10'], EmittingPathDataHandler(emitter))()

        emitter.emit_move_to.assert_called_once_with(0, 10)
        emitter.emit_line_to.assert_called_once_with(0, 20)

    def test_V(self):
        from .convert import EmittingPathDataHandler
        from altair.svg.path import PathDataScanner

        emitter = Mock()
        PathDataScanner(['m', '0', '10', 'V', '20'], EmittingPathDataHandler(emitter))()

        emitter.emit_move_to.assert_called_once_with(0, 10)
        emitter.emit_line_to.assert_called_once_with(0, 20)

    def test_a(self):
        from .convert import EmittingPathDataHandler
        from altair.svg.path import PathDataScanner

        emitter = Mock()
        PathDataScanner(['m', '0', '10', 'a', '20', '20', '3.', '1', '1', '20', '30'], EmittingPathDataHandler(emitter))()

        emitter.emit_move_to.assert_called_once_with(0, 10)
        emitter.emit_arc.assert_called_once_with(20., 20., 3., True, True, 20., 40.)

    def test_A(self):
        from .convert import EmittingPathDataHandler
        from altair.svg.path import PathDataScanner

        emitter = Mock()
        PathDataScanner(['m', '0', '10', 'A', '20', '20', '3', '1', '1', '20', '30'], EmittingPathDataHandler(emitter))()

        emitter.emit_move_to.assert_called_once_with(0, 10)
        emitter.emit_arc.assert_called_once_with(20., 20., 3., True, True, 20., 30.)
