import openpyxl

class XlsxTabularDataReader(object):
    def __init__(self, exts, names):
        self.exts = exts
        self.names = names

    def open(self, f, **options):
        wb = openpyxl.load_workbook(f)
        ws = wb.active
        return (
            [col.value for col in row]
            for row in ws.rows
            )



class XlsxTabularDataWriter(object):
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
            self.ws.append(cols)
            self.r += 1    


    def __init__(self, exts, names):
        self.exts = exts
        self.names = names

    def open(self, f, encoding=u'UTF-8', sheet_name=u'Sheet1', **options):
        wb = openpyxl.Workbook(encoding=encoding, write_only=True)
        ws = wb.create_sheet(sheet_name)
        return Helper(wb, ws, f)
