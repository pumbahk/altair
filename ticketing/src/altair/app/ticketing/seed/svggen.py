# encoding: utf-8

from lxml.etree import Element, SubElement

SVG_NAMESPACE = 'http://www.w3.org/2000/svg'

class NESW(object):
    def __init__(self, top=0., right=0., bottom=0., left=0.):
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left

class SVGGenerator(object):
    def __init__(self, seat_size, margin, padding, row_margin):
        self.seat_size = seat_size
        self.margin = margin
        self.padding = padding
        self.row_margin = row_margin

    def __call__(self, config):
        colgroups = config['colgroups']
        seats_per_row = config['seats_per_row']

        row_width = self.seat_size * seats_per_row + \
            self.row_margin.right + self.row_margin.left
        row_height = self.seat_size + self.row_margin.top + self.row_margin.bottom
        doc_width = self.margin.right + self.margin.left + \
            self.padding.right + self.padding.left + \
            len(colgroups) * row_width
        doc_height = self.margin.top + self.margin.bottom + \
            self.padding.top + self.padding.bottom + \
            ((reduce(lambda prev, colgroup: max(prev, len(colgroup[2])), colgroups, 0) +
             seats_per_row - 1) / seats_per_row) * row_height
        doc = Element(u"{%s}svg" % SVG_NAMESPACE,
                      nsmap={None:SVG_NAMESPACE},
                      version=u'1.0',
                      width=u'%d' % doc_width,
                      height=u'%d' % doc_height,
                      viewbox=u"%d %d %d %d" % (0, 0, doc_width, doc_height))
        style_node = SubElement(doc, u"{%s}style" % SVG_NAMESPACE)
        style_node.text = """
.seat { stroke: #000000; stroke-width: 1px; fill: #ffffff }
"""
        body_node = SubElement(doc, u"{%s}g" % SVG_NAMESPACE)

        outermost_box = SubElement(
            body_node,
            u"{%s}rect" % SVG_NAMESPACE,
            x=u"%d" % self.margin.left,
            y=u"%d" % self.margin.top,
            width=u"%d" % (doc_width - self.margin.left - self.margin.top),
            height=u"%d" % (doc_height - self.margin.top - self.margin.bottom)
            )
        outermost_box.set(u'fill', u'none')
        outermost_box.set(u'stroke', u'#000000')
        outermost_box.set(u'stroke-width', u'1px')

        for colgroup_num, (colgroup_name, colgroup_id, seats_in_colgroup) in enumerate(colgroups):
            colgroup_node = SubElement(
                body_node,
                u"{%s}g" % SVG_NAMESPACE,
                id=colgroup_id)
            num_seats = len(seats_in_colgroup)
            for row_num in range(0, (num_seats + seats_per_row - 1) / seats_per_row):
                row_node = SubElement(
                    colgroup_node,
                    u"{%s}g" % SVG_NAMESPACE,
                    id=u"row-%s-%d" % (colgroup_name, row_num + 1))
                ox = self.margin.left + self.padding.left +\
                    colgroup_num * row_width + self.row_margin.left
                y = self.margin.top + self.padding.top +\
                    row_num * row_height + self.row_margin.top
                for col_num in range(0, seats_per_row):
                    seat_index = col_num + row_num * seats_per_row
                    if seat_index >= num_seats:
                        continue
                    x = ox + col_num * self.seat_size
                    seat_node = SubElement(
                        row_node,
                        u"{%s}rect" % SVG_NAMESPACE,
                        id=seats_in_colgroup[row_num * seats_per_row + col_num])
                    seat_node.set(u"class", u"seat")
                    seat_node.set(u'x', u"%d" % x)
                    seat_node.set(u'y', u"%d" % y)
                    seat_node.set(u'width', u"%d" % self.seat_size)
                    seat_node.set(u'height', u"%d" % self.seat_size)
             
        return doc


if __name__ == '__main__':
    from lxml.etree import tostring
    print tostring(
        SVGGenerator(
            seat_size=10,
            margin=NESW(top=4., right=4., bottom=4., left=4.),
            padding=NESW(top=4., right=4., bottom=4., left=4.),
            row_margin=NESW(top=4., right=4., bottom=4., left=4.),
        )(dict(colgroups=[
            (u'A', u'colgroup-A', [u'1', u'2', u'3']),
            (u'B', u'colgroup-B', [u'4', u'5']),
            (u'C', u'colgroup-C', [u'6', u'7'])
            ])),
        pretty_print=True)
