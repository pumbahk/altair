import logging
import re
from dateutil import parser
logger = logging.getLogger(__file__)

class SejFileParser(object):

    class SejFileParserRow(object):
        cursor = 0
        #
        def __init__(self, row):
            self.row = row
        #
        def get_col(self, num):
            row = self.row[self.cursor:self.cursor+num]
            self.cursor = self.cursor + num
            return row

        def get_int(self, num):
            col = self.get_col(num).replace(' ', '')
            return int(col) if len(col) else None

        def get_datetime(self, num):
            col = self.get_col(num).replace(' ', '')
            return parser.parse(col) if len(col) else None

    rec_segment = ''
    shop_id     = ''
    filename    = ''
    date        = ''
    row_length  = 0
    row_count   = 0

    def parse_header(self, row):
        self.rec_segment = row.get_col(1)
        if self.rec_segment != 'H':
            raise Exception("Invalid header type : %s" % self.rec_segment)
        self.shop_id     = row.get_col(5)
        self.filename    = row.get_col(30)
        self.date        = row.get_col(8)
        self.row_length  = int(row.get_col(4))

    def parse_footer(self, row):
        self.row_count   = int(row.get_col(6))

    def parse_row(self, row):
        raise Exception("stub: method not implements.")

    def parse(self, data):

        self.parse_header(SejFileParser.SejFileParserRow(data))
        total_length = len(data)

        if total_length % self.row_length != 0:
            raise Exception('Invalid row length  row:%d total:%d' % (self.row_length, total_length))

        values = []

        for start_at in range(self.row_length, len(data),self.row_length):
            row = data[start_at : start_at + self.row_length]
            row_obj = SejFileParser.SejFileParserRow(row)
            row_type = row_obj.get_col(1)
            if row_type == 'E':
                self.parse_footer(row_obj)
                break
            values.append(self.parse_row(row_obj))

        if not self.row_count:
            raise Exception('Invalid row footer row:%d total:%d' % (self.row_length, total_length))
        if self.row_count != len(values)+2:
            raise Exception('Invalid row count count:%d/%d row:%d total:%d' % (self.row_count, len(values), self.row_length, total_length))

        return values
