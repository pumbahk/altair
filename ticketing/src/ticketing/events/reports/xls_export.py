# -*- coding: utf-8 -*-
from StringIO import StringIO
import copy

import xlwt
import xlrd
from xlwt.Style import XFStyle
from xlwt.Cell import StrCell
from xlutils.filter import process, XLRDReader, XLWTWriter


def isStrCell(cell):
    """文字列のCellであればTrueを返す
    """
    return isinstance(cell, xlwt.Cell.StrCell)


def get_cell(sheet, row_index, colx):
    """指定したシートの指定した行、列のセルを返す
    """
    row = sheet.row(row_index)
    return row._Row__cells.get(colx)


def get_cells(sheet, row_index):
    """シートの指定した行のセル(idx, value)を返す
    """
    row = sheet.row(row_index)
    return row._Row__cells.items()


def get_merged_ranges_for_row(row_index, sheet):
    """row_indexで指定した行のマージ情報をタプルで返す
    sheet: シート
    """
    result = []
    for tpl in sheet.merged_ranges:
        if tpl[0] == row_index:
            result.append(tpl)
    return result


def get_merged_range_for_cell(row_index, col_index, sheet):
    """row_index, col_indexで指定した位置のマージ情報をタプルで返す
    sheet: シート
    """
    for tpl in sheet.merged_ranges:
        if tpl[0] == row_index and tpl[2] == col_index:
            return tpl


def add_merged_range_to_sheet(sheet, merged_range):
    """マージ情報をシートに追加する
    """
    sheet._Worksheet__merged_ranges.append(merged_range)


def xl_copy(wb):
    """
    xlutils.copy.copy関数でWriterを返すようにしたもの
    """
    w = XLWTWriter()
    process(
        XLRDReader(wb, 'unknown.xls'),
        w
        )
    return w.output[0][1], w


def get_str_from_cell(cell, workbook):
    """指定したセルの文字列を返す
    """
    if not isStrCell(cell):
        return None
    for s, idx in workbook._Workbook__sst._str_indexes.items():
        if idx == cell.sst_idx:
            return s


def get_style_by_xf_index(idx, workbook):
    """指定したxf_indexのStyleを返す
    """
    style = XFStyle()
    for xf, xf_index in workbook._Workbook__styles._xf_id2x.items():
        if xf_index == idx:
            style.alignment = xf[2]
            style.borders = xf[3]
            style.pattern = xf[4]
            style.protection = xf[5]
            for font, font_idx in workbook._Workbook__styles._font_id2x.items():
                if font_idx == xf[0]:
                    style.font = font
            for num_format_str, num_format_idx in workbook._Workbook__styles._num_formats.items():
                if num_format_idx == xf[1]:
                    style.num_format_str = num_format_str
            break
    return style


class BaseExporter(object):
    def __init__(self, template):
        """
        template: テンプレートExcelファイル
        """
        self.template = template
        self.read_buffer = xlrd.open_workbook(
            self.template, formatting_info=True)
        self.workbook, self.xl_writer = xl_copy(self.read_buffer)

    def as_string(self):
        """文字列で返す
        """
        sio = StringIO()
        self.workbook.save(sio)
        return sio.getvalue()

    def get_sheets(self):
        """ワークシートを返す
        """
        return self.workbook._Workbook__worksheets

    def get_style_from_cell(self, cell):
        """指定したCellのStyleを返す
        """
        return self.xl_writer.style_list[cell.xf_idx]

    def remove_sheet(self, index):
        # シートのリストから指定した位置のシートを削除
        sheet = self.workbook._Workbook__worksheets.pop(index)
        # シート名からのインデックスを削除
        del self.workbook._Workbook__worksheet_idx_from_name[sheet.name]

    def add_sheet(self, sheetname):
        """シートの1つ目をコピーして増やす
        """
        lower_name = sheetname.lower()
        if lower_name in self.workbook._Workbook__worksheet_idx_from_name:
            raise Exception("duplicate worksheet name %r" % sheetname)
        # ワークブックからシートをコピー
        new_buffer, _ = xl_copy(self.read_buffer)
        new_sheet = new_buffer.get_sheet(0)
        new_sheet.name = sheetname
        # 親オブジェクト貼り替え
        for row in new_sheet._Worksheet__rows.values():
            row._Row__parent_wb = self.workbook
        for col in new_sheet._Worksheet__cols.values():
            col._Row__parent_wb = self.workbook
        tmp_workbook = new_sheet._Worksheet__parent
        new_sheet._Worksheet__parent = self.workbook
        self.workbook._Workbook__worksheet_idx_from_name[lower_name] = len(self.workbook._Workbook__worksheets)
        self.workbook._Workbook__worksheets.append(new_sheet)
        # 文字列テーブルの参照カウント更新
        for k, v in tmp_workbook._Workbook__sst._str_indexes.items():
            for i in range(tmp_workbook._Workbook__sst._tally[v]):
                self.workbook._Workbook__sst.add_str(k)
        return new_sheet

    def get_row_data(self, sheet, row_index):
        """行を保持するためのデータを辞書で返す
        Cell, Style, merged_ranges
        """
        cells = [cell for idx, cell in get_cells(sheet, row_index)]
        styles = [get_style_by_xf_index(cell.xf_idx, self.workbook) if cell else None for cell in cells]
        merged_ranges = get_merged_ranges_for_row(row_index, sheet)
        result = {
            'cells': cells,
            'styles': styles,
            'merged_ranges': merged_ranges,
        }
        return result

    def write_row_data(self, sheet, row_index, cells=None, styles=None, merged_ranges=None):
        """行データを書き込み
        """
        if cells is None:
            cells = []
        if styles is None:
            styles = []
        if merged_ranges is None:
            merged_ranges = []
        row = sheet.row(row_index)
        for i, cell, style in zip(range(len(cells)), cells, styles):
            copied_cell = copy.copy(cell)
            if cell != None:
                copied_style = copy.copy(style)
                xf_index = self.workbook.add_style(style)
                copied_cell.rowx = row_index
                copied_cell.xf_idx = xf_index
                # 文字列の場合は参照カウント増やす
                if isinstance(copied_cell, StrCell):
                    self.workbook._Workbook__sst._tally[copied_cell.sst_idx] += 1
            row.insert_cell(i, copied_cell)
        # セルの結合情報をコピー
        for tpl in merged_ranges:
            new_range = list(tpl)
            new_range[0] = row_index
            new_range[1] = row_index
            add_merged_range_to_sheet(sheet, new_range)

    def update_cell_text(self, sheet, row_index, colx, text):
        """指定したセルのテキストを更新(Styleは保持)
        """
        self.workbook._Workbook__sst.add_str(text)
        cell = get_cell(sheet, row_index, colx)
        if cell is None:
            style = XFStyle()
        else:
            style = get_style_by_xf_index(cell.xf_idx, self.workbook)
        row = sheet.row(row_index)
        row.write(colx, text, style)
        cell = get_cell(sheet, row_index, colx)


class SalesScheduleReportExporter(BaseExporter):
    """販売日程管理票の帳票出力(Excel)
    """
    def __init__(self, template):
        super(SalesScheduleReportExporter, self).__init__(template)

    def remove_templates(self):
        "先頭から2つのテンプレート用のシートを削除"
        self.remove_sheet(0)
        self.remove_sheet(0)

    def write_output_datetime(self, sheet, value):
        self.update_cell_text(sheet, 0, 12, value)

    def write_event_title(self, sheet, value):
        self.update_cell_text(sheet, 4, 0, value)

    def write_data(self, sheet, data):
        """シートにデータを流し込む
        {
          'event_title': value,
          'output_datetime': value,
          'sales': [{}],
          'performances': [{}],
          'price_blocks': [{'prices': [{}]}],
        }
        """
        event_title = data.get('event_title')
        if event_title:
            self.write_event_title(sheet, event_title)
        output_datetime = data.get('output_datetime')
        if output_datetime:
            self.write_output_datetime(sheet, output_datetime)


class SeatAssignExporter(BaseExporter):
    """座席管理票の帳票出力
    """
    def __init__(self, template):
        super(SeatAssignExporter, self).__init__(template)
        self._seat_header_rows = self.get_seat_header_rows()
        self._seat_footer_rows = self.get_seat_footer_rows()
        self._record_row = self.get_record_row()
        self.current_pos = {}
        self.current_pos[self.workbook.get_sheet(0)] = 11
        # 文字列テーブルの参照カウントを増やしておく
        for k, v in self.workbook._Workbook__sst._str_indexes.items():
            self.workbook._Workbook__sst.add_str(k)

    def get_seat_header_rows(self):
        """席種ごとの可変部分のヘッダ
        """
        result = []
        sheet = self.workbook.get_sheet(0)
        for i in [11, 12, 13]:
            result.append(self.get_row_data(sheet, i))
        return result

    def get_seat_footer_rows(self):
        """席種ごとの可変部分のフッタ
        """
        result = []
        sheet = self.workbook.get_sheet(0)
        for i in [15, 16, 17, 18]:
            result.append(self.get_row_data(sheet, i))
        return result

    def get_record_row(self):
        """レコード追加用の行
        """
        sheet = self.workbook.get_sheet(0)
        return self.get_row_data(sheet, 14)

    def write_seat_header(self, sheet):
        """席種のヘッダを書き込む
        """
        num_header = len(self._seat_header_rows)
        pos = self.current_pos.get(sheet, 11)
        for i, row_data in zip(range(pos, pos + num_header), self._seat_header_rows):
            self.write_row_data(
                sheet,
                i,
                cells=row_data['cells'],
                styles=row_data['styles'],
                merged_ranges=row_data['merged_ranges'],
            )
        self.current_pos[sheet] = pos + num_header

    def write_seat_footer(self, sheet):
        """席種のヘッダを書き込む
        """
        num_footer = len(self._seat_footer_rows)
        pos = self.current_pos.get(sheet, 11)
        for i, row_data in zip(range(pos, pos + num_footer), self._seat_footer_rows):
            self.write_row_data(
                sheet,
                i,
                cells=row_data['cells'],
                styles=row_data['styles'],
                merged_ranges=row_data['merged_ranges'],
            )
        self.current_pos[sheet] = pos + num_footer + 1

    def write_record_row(self, sheet, record):
        """行の書き込み
        """
        row_data = self._record_row
        cells = list(self._record_row['cells'])
        pos = self.current_pos.get(sheet, 11)
        # ブロック
        if record.get('block'):
            cells[0] = StrCell(
                pos,
                0,
                cells[0].xf_idx,
                self.workbook.add_str(record.get('block')))
        # 列
        if record.get('line'):
            cells[5] = StrCell(
                pos,
                5,
                cells[5].xf_idx,
                self.workbook.add_str(record.get('line')))
        # 仕入席数
        if record.get('stocks'):
            stocks = record.get('stocks', [])
            for i, value in enumerate(stocks):
                cells[6 + i] = StrCell(
                    pos,
                    6 + i,
                    cells[6 + i].xf_idx,
                    self.workbook.add_str(value))
        # 返券席数
        if record.get('returns'):
            returns = record.get('returns', [])
            for i, value in enumerate(returns):
                cells[10 + i] = StrCell(
                    pos,
                    10 + i,
                    cells[10 + i].xf_idx,
                    self.workbook.add_str(value))
        # シートに書き込み
        self.write_row_data(
            sheet,
            pos,
            cells=cells,
            styles=row_data['styles'],
            merged_ranges=row_data['merged_ranges'],
        )
        self.current_pos[sheet] = pos + 1

    def set_id(self, sheet, value):
        """番号の入力
        """
        self.update_cell_text(sheet, 0, 13, value)

    def set_stock_holder_name(self, sheet, value):
        """取引先名の入力
        """
        self.update_cell_text(sheet, 2, 0, value)

    def set_datetime(self, sheet, value):
        """日時
        """
        self.update_cell_text(sheet, 1, 11, value)

    def set_event_name(self, sheet, value):
        """イベント名
        """
        self.update_cell_text(sheet, 7, 0, value)

    def set_performance_datetime(self, sheet, value):
        """パフォーマンス日時
        """
        self.update_cell_text(sheet, 9, 0, value)

    def set_performance_name(self, sheet, value):
        """パフォーマンス名
        """
        self.update_cell_text(sheet, 9, 7, value)

    def add_records(self, sheet, data):
        """シートに席種ごとのデータを追加する
        """
        self.write_seat_header(sheet)
        # 席種
        seattype = data.get('seattype')
        if seattype:
            seattype_rowx = self.current_pos[sheet] - 3
            self.update_cell_text(sheet, seattype_rowx, 0, seattype)
        # 仕入席数のラベル
        stocks_label = data.get('stocks_label')
        if stocks_label:
            stocks_label_rowx = self.current_pos[sheet] - 2
            self.update_cell_text(sheet, stocks_label_rowx, 6, stocks_label)
        # レコード書き込み
        for record in data.get('records', []):
            self.write_record_row(sheet, record)
        self.write_seat_footer(sheet)
        # 仕入れ席数(計)
        total1 = data.get('total1')
        if total1:
            total1_rowx = self.current_pos[sheet] - 2
            self.update_cell_text(sheet, total1_rowx, 9, total1)
        # 返券席数(計)
        total2 = data.get('total2')
        if total2:
            total2_rowx = self.current_pos[sheet] - 2
            self.update_cell_text(sheet, total2_rowx, 14, total2)
