# encoding: utf-8

import re

class PathDataScanner(object):
    def __init__(self, iter, handler):
        self.iter = iter
        self.handler = handler
        self.current_position = (0, 0)
        self.last_qb_control_point = None
        self.last_cb_control_point = None
        self.next_op = None

    def scan_z(self, operand):
        if len(operand) > 0:
            raise Exception('closepath does not take any arguments')
        self.handler.close_path()
        self.last_qb_control_point = None
        self.last_cb_control_point = None

    scan_Z = scan_z

    def scan_h(self, operand):
        if len(operand) == 0:
            raise Exception('horizontalline takes at least 1 argument')
        for oper in operand:
            x = self.current_position[0] + float(oper)
            self.handler.line_to(x, self.current_position[1])
            self.current_position = (x, self.current_position[1])
        self.last_qb_control_point = None
        self.last_cb_control_point = None

    def scan_H(self, operand):
        if operand == 0:
            raise Exception('horizontalline takes at least 1 argument')
        for oper in operand:
            x = float(oper)
            self.handler.line_to(x, self.current_position[1])
            self.current_position = (x, self.current_position[1])
        self.last_qb_control_point = None
        self.last_cb_control_point = None

    def scan_v(self, operand):
        if len(operand) == 0:
            raise Exception('verticalline takes at least 1 argument')
        for oper in operand:
            y = self.current_position[1] + float(oper)
            self.handler.line_to(self.current_position[0], y)
            self.current_position = (self.current_position[0], y)
        self.last_qb_control_point = None
        self.last_cb_control_point = None

    def scan_V(self, operand):
        if len(operand) == 0:
            raise Exception('verticalline takes at least 1 argument')
        for oper in operand:
            y = float(oper)
            self.handler.line_to(self.current_position[0], y)
            self.current_position = (self.current_position[0], y)
        self.last_qb_control_point = None
        self.last_cb_control_point = None

    def scan_m(self, operand):
        if operand == 0 or len(operand) % 2 != 0:
            raise Exception('moveto takes 2 * n arguments')
        i = iter(operand)
        try:
            x = self.current_position[0] + float(i.next())
            y = self.current_position[1] + float(i.next())
            self.handler.move_to(x, y)
            self.current_position = (x, y)
            while True:
                x = self.current_position[0] + float(i.next())
                y = self.current_position[1] + float(i.next())
                self.handler.line_to(x, y)
                self.current_position = (x, y)
        except StopIteration:
            pass
        self.last_qb_control_point = None
        self.last_cb_control_point = None

    def scan_M(self, operand):
        if operand == 0 or len(operand) % 2 != 0:
            raise Exception('moveto takes 2 * n arguments')
        i = iter(operand)
        try:
            x = float(i.next())
            y = float(i.next())
            self.handler.move_to(x, y)
            self.current_position = (x, y)
            while True:
                x = float(i.next())
                y = float(i.next())
                self.handler.line_to(x, y)
                self.current_position = (x, y)
        except StopIteration:
            pass
        self.last_qb_control_point = None
        self.last_cb_control_point = None

    def scan_l(self, operand):
        if operand == 0 or len(operand) % 2 != 0:
            raise Exception('lineto takes 2 * n arguments')
        i = iter(operand)
        try:
            while True:
                x = self.current_position[0] + float(i.next())
                y = self.current_position[1] + float(i.next())
                self.handler.line_to(x, y)
                self.current_position = (x, y)
        except StopIteration:
            pass
        self.last_qb_control_point = None
        self.last_cb_control_point = None

    def scan_L(self, operand):
        if operand == 0 or len(operand) % 2 != 0:
            raise Exception('lineto takes 2 * n arguments')
        i = iter(operand)
        try:
            while True:
                x = float(i.next())
                y = float(i.next())
                self.handler.line_to(x, y)
                self.current_position = (x, y)
        except StopIteration:
            pass
        self.last_qb_control_point = None
        self.last_cb_control_point = None

    def scan_t(self, operand):
        if operand == 0 or len(operand) % 2 != 0:
            raise Exception('curvetosmooth takes 2 * n arguments')
        i = iter(operand)
        try:
            while True:
                x = self.current_position[0] + float(i.next())
                y = self.current_position[1] + float(i.next())
                if self.last_qb_control_point is None:
                    x1 = self.current_position[0]
                    y1 = self.current_position[1]
                else:
                    x1 = self.current_position[0] + (self.current_position[0] - self.last_qb_control_point[0])
                    y1 = self.current_position[1] + (self.current_position[1] - self.last_qb_control_point[1])
                self.handler.curve_to_qb(x1, y1, x, y)
                self.current_position = (x, y)
                self.last_qb_control_point = (x1, y1)
        except StopIteration:
            pass
        self.last_cb_control_point = None

    def scan_T(self, operand):
        if operand == 0 or len(operand) % 2 != 0:
            raise Exception('curvetosmooth takes 2 * n arguments')
        i = iter(operand)
        try:
            while True:
                x = float(i.next())
                y = float(i.next())
                if self.last_qb_control_point is None:
                    x1 = self.current_position[0]
                    y1 = self.current_position[1]
                else:
                    x1 = self.current_position[0] + (self.current_position[0] - self.last_qb_control_point[0])
                    y1 = self.current_position[1] + (self.current_position[1] - self.last_qb_control_point[1])
                self.handler.curve_to_qb(x1, y1, x, y)
                self.current_position = (x, y)
                self.last_qb_control_point = (x1, y1)
        except StopIteration:
            pass
        self.last_cb_control_point = None

    def scan_s(self, operand):
        if operand == 0 or len(operand) % 4 != 0:
            raise Exception('curvetosmooth takes 4 * n arguments')
        i = iter(operand)
        try:
            while True:
                if self.last_cb_control_point is None:
                    x1 = self.current_position[0]
                    y1 = self.current_position[1]
                else:
                    x1 = self.current_position[0] + (self.current_position[0] - self.last_cb_control_point[0])
                    y1 = self.current_position[1] + (self.current_position[1] - self.last_cb_control_point[1])
                x2 = self.current_position[0] + float(i.next())
                y2 = self.current_position[1] + float(i.next())
                x = self.current_position[0] + float(i.next())
                y = self.current_position[1] + float(i.next())
                self.handler.curve_to(x1, y1, x2, y2, x, y)
                self.current_position = (x, y)
                self.last_cb_control_point = (x2, y2)
        except StopIteration:
            pass
        self.last_qb_control_point = None

    def scan_S(self, operand):
        if operand == 0 or len(operand) % 4 != 0:
            raise Exception('curvetosmooth takes 4 * n arguments')
        i = iter(operand)
        try:
            while True:
                if self.last_cb_control_point is None:
                    x1 = self.current_position[0]
                    y1 = self.current_position[1]
                else:
                    x1 = self.current_position[0] + (self.current_position[0] - self.last_cb_control_point[0])
                    y1 = self.current_position[1] + (self.current_position[1] - self.last_cb_control_point[1])
                x2 = float(i.next())
                y2 = float(i.next())
                x = float(i.next())
                y = float(i.next())
                self.handler.curve_to(x1, y1, x2, y2, x, y)
                self.current_position = (x, y)
                self.last_cb_control_point = (x2, y2)
        except StopIteration:
            pass
        self.last_qb_control_point = None

    def scan_q(self, operand):
        if operand == 0 or len(operand) % 4 != 0:
            raise Exception('curvetoqb takes 4 * n arguments')
        i = iter(operand)
        try:
            while True:
                x1 = self.current_position[0] + float(i.next())
                y1 = self.current_position[1] + float(i.next())
                x = self.current_position[0] + float(i.next())
                y = self.current_position[1] + float(i.next())
                self.last_qb_control_point = (x1, y1)
                self.handler.curve_to_qb(x1, y1, x, y)
                self.current_position = (x, y)
        except StopIteration:
            pass
        self.last_cb_control_point = None

    def scan_Q(self, operand):
        if operand == 0 or len(operand) % 4 != 0:
            raise Exception('curvetoqb takes 4 * n arguments')
        i = iter(operand)
        try:
            while True:
                x1 = float(i.next())
                y1 = float(i.next())
                x = float(i.next())
                y = float(i.next())
                self.last_qb_control_point = (x1, y1)
                self.handler.curve_to_qb(x1, y1, x, y)
                self.current_position = (x, y)
        except StopIteration:
            pass
        self.last_cb_control_point = None

    def scan_c(self, operand):
        if operand == 0 or len(operand) % 6 != 0:
            raise Exception('curveto takes 6 * n arguments')
        i = iter(operand)
        try:
            while True:
                x1 = self.current_position[0] + float(i.next())
                y1 = self.current_position[1] + float(i.next())
                x2 = self.current_position[0] + float(i.next())
                y2 = self.current_position[1] + float(i.next())
                x = self.current_position[0] + float(i.next())
                y = self.current_position[1] + float(i.next())
                self.handler.curve_to(x1, y1, x2, y2, x, y)
                self.current_position = (x, y)
                self.last_cb_control_point = (x2, y2)
        except StopIteration:
            pass
        self.last_qb_control_point = None

    def scan_C(self, operand):
        if operand == 0 or len(operand) % 6 != 0:
            raise Exception('curveto takes 6 * n arguments')
        i = iter(operand)
        try:
            while True:
                x1 = float(i.next())
                y1 = float(i.next())
                x2 = float(i.next())
                y2 = float(i.next())
                x = float(i.next())
                y = float(i.next())
                self.handler.curve_to(x1, y1, x2, y2, x, y)
                self.current_position = (x, y)
                self.last_cb_control_point = (x2, y2)
        except StopIteration:
            pass
        self.last_qb_control_point = None

    def scan_a(self, operand):
        if operand == 0 or len(operand) % 7 != 0:
            raise Exception('arc takes 7 * n arguments')
        i = iter(operand)
        try:
            while True:
                rx = float(i.next())
                ry = float(i.next())
                phi = float(i.next())
                largearc = bool(i.next())
                sweep = bool(i.next())
                x = self.current_position[0] + float(i.next())
                y = self.current_position[1] + float(i.next())
                self.handler.arc(rx, ry, phi, largearc, sweep, x, y)
                self.current_position = (x, y)
        except StopIteration:
            pass
        self.last_cb_control_point = None
        self.last_qb_control_point = None

    def scan_A(self, operand):
        if operand == 0 or len(operand) % 7 != 0:
            raise Exception('arc takes 7 * n arguments')
        i = iter(operand)
        try:
            while True:
                rx = float(i.next())
                ry = float(i.next())
                phi = float(i.next())
                largearc = bool(i.next())
                sweep = bool(i.next())
                x = float(i.next())
                y = float(i.next())
                self.handler.arc(rx, ry, phi, largearc, sweep, x, y)
                self.current_position = (x, y)
        except StopIteration:
            pass
        self.last_cb_control_point = None
        self.last_qb_control_point = None

    def __call__(self):
        fn = None
        operand = []
        for op in self.iter:
            next_fn = getattr(self, 'scan_' + op, None)
            if fn is not None:
                if next_fn is not None:
                    fn(operand)
                    fn = next_fn
                    operand = []
                else:
                    operand.append(op)
            else:
                fn = next_fn
        if fn is not None:
            fn(operand)

NUM_REGEX = ur'(-?(?:(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)(?:[eE][-+]?[0-9]+)?))'

def tokenize_path_data(path):
    return (g.group(0) for g in re.finditer(NUM_REGEX + ur'|[A-Za-z_]+', path))

def parse_poly_data(poly):
    return ((float(g.group(1)), float(g.group(2))) for g in re.finditer(NUM_REGEX + ur'(?:\s+(?:,\s*)?|,\s*)' + NUM_REGEX, poly))
