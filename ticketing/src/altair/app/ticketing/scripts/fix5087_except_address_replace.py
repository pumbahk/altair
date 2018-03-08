#-*- coding: utf-8 -*-
#!/usr/bin/env python
import os
import re
import sys
import csv
import zenhan
from collections import namedtuple

LotData = namedtuple('LotData',
    'status entry_no wish created_at stock_type quantity event venue performance code start_on product payment_method delivery_method last_name first_name last_name_kana first_name_kana zip country prefecture city address1 address2 tel1 tel2 fax mail1 mail2 sex birthday memo last_name2 first_name2 last_name2_kana first_name2_kana nickname profile_sex profile_birthday channel browserid membership_name membergroup_name membergroup_id')


def format_address(address):
    # チョップ、丁目、番地、番、ハイフン、文字化け、全角半角、波線、イコール
    address = address.strip()
    address = zenhan.z2h(unicode(address, 'UTF-8'), 3).encode('utf-8')
    address = address.replace("ー", "-")
    address = address.replace("~", "-")
    address = address.replace("=", "-")
    address = address.replace("?", "-")
    address = address.replace("丁目", "-")
    address = address.replace("番", "")
    address = address.replace("番地", "")
    address = address.replace("号", "")
    # 住所から「３の２の１」みたいな「の」を弾く処理が動いていない
    # match = re.search(r'\d', address)
    # if match:
    #     # 数字が出現したあとの文字列
    #     target = address[match.start():].replace("の", "-")
    #     address = "{0}{1}".format(address[0:match.start()-1], target)
    return address


def except_duplicate_address(target_row, wrong_writer, elect_file):
    # 住所
    target_address = format_address(target_row.city, target_row.address1, target_row.address2)
    with open(elect_file, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)

        for row in reader:
            lot_data = LotData._make(row)
            address = format_address(lot_data.city, lot_data.address1, lot_data.address2)
            if address == target_address:
                address_writer = wrong_writer['address']
                address_writer.writerow(target_row)
                return False
    return True


def main(argv=sys.argv[1:]):
    # 抽選申込ファイルの住所をキレイにするスクリプト
    # 住所の全角ハイフンを、半角ハイフンにする
    # 住所のはてなを、半角ハイフンにする
    # 住所の「３の１の２」みたいなものを「3-1-2」にする
    # 引数：フォルダパス、結果ファイル名、抽選申込ファイル
    result_file = "{0}{1}".format(argv[0], argv[1]) # 抽選申込ファイル
    input_file = "{0}{1}".format(argv[0], argv[2]) # 抽選申込ファイル

    # 入力ファイル、当選ファイルをエクセルで読めるSJIS -> UTF8へ変換
    os.system('nkf -w --overwrite {0}'.format(input_file))

    if os.path.isfile(result_file):
        os.remove(result_file)
    out = open(result_file, 'w')
    writer = csv.writer(out, lineterminator='\n')

    with open(input_file, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        writer.writerow(header)

        for row in reader:
            row[21] = format_address(row[21])
            row[22] = format_address(row[22])
            row[23] = format_address(row[23])
            writer.writerow(row)

    out.close()
    print "start address replace script"
    os.system('nkf -s --overwrite {0}'.format(input_file))
    os.system('nkf -s --overwrite {0}'.format(result_file))

    print "end address replace script"


if __name__ == '__main__':
    main()
