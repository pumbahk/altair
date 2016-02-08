from six import text_type

PREFERRED_MIME_TYPE = 'application/vnd.ms-excel'

class XlsTabularDataReader(object):
    preferred_mime_type = PREFERRED_MIME_TYPE

    def __init__(self, exts, names):
        self.exts = exts
        self.names = names

    def open(self, f, sheet=None, encoding=None, **options):
        import xlrd
        kwargs = {}
        if encoding is not None:
            kwargs['encoding_override'] = encoding
        if isinstance(f, (str, text_type)):
            wb = xlrd.open_workbook(f, **kwargs)
        else:
            wb = xlrd.open_workbook(file_contents=f.read(), **kwargs)
        if sheet is not None:
            ws = wb.sheet_by_name(sheet)
        else:
            for ws in wb.sheets():
                if ws.sheet_selected:
                    break
            else:
                ws = wb.sheets[0]
        return (
            tuple(
                ws.col(col_index, row_index)[0].value
                for col_index in range(0, ws.ncols)
                )
            for row_index in range(0, ws.nrows)
            )


class XlsTabularDataWriter(object):
    preferred_mime_type = PREFERRED_MIME_TYPE

    class Helper(object):
        def __init__(self, wb, ws, f):
            self.wb = wb
            self.ws = ws
            self.f = f
            self.r = 0

        def close(self):
            if self.wb is not None:
                self.wb.save(self.f)
            self.wb = self.ws = None

        def __call__(self, cols):
            for c, col in enumerate(cols):
                self.ws.write(self.r, c, col)
            self.r += 1


    def __init__(self, exts, names):
        self.exts = exts
        self.names = names

    def open(self, f, sheet=None, encoding=u'ascii', style_compression=False, sheet_name=u'Sheet1', **options):
        from xlwt.Workbook import Workbook
        wb = Workbook(encoding=encoding, style_compression=style_compression)
        ws = wb.add_sheet(sheet_name)
        return self.Helper(wb, ws, f) 
