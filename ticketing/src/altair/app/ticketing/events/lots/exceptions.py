# -*- coding:utf-8 -*-

class CSVFileParserError(Exception):
    def __init__(self, entry_no, *args, **kwargs):
        super(CSVFileParserError, self).__init__(*args, **kwargs)
        self.entry_no = entry_no
