#-*- coding: utf-8 -*-
#!/usr/bin/env python
import os
import sys
import csv
from collections import namedtuple

"""
-    STAGE FES 2017／アンケート（お目当て）
-    10960
LotData = namedtuple('LotData',
    'status entry_no wish created_at stock_type quantity event venue performance code start_on product payment_method delivery_method last_name first_name last_name_kana first_name_kana zip country prefecture city address1 address2 tel1 tel2 fax mail1 mail2 sex birthday memo last_name2 first_name2 last_name2_kana first_name2_kana nickname profile_sex profile_birthday channel browserid membership_name membergroup_name membergroup_id like_artist')


-    ANiUTa（利用者ID、お目当て）
-    10962
LotData = namedtuple('LotData',
    'status entry_no wish created_at stock_type quantity event venue performance code start_on product payment_method delivery_method last_name first_name last_name_kana first_name_kana zip country prefecture city address1 address2 tel1 tel2 fax mail1 mail2 sex birthday memo last_name2 first_name2 last_name2_kana first_name2_kana nickname profile_sex profile_birthday channel browserid membership_name membergroup_name membergroup_id user_id like_artist')

-    ニコニコ
-    11020, 11019, 11003, 11001, 10997,
LotData = namedtuple('LotData',
    'status entry_no wish created_at stock_type quantity event venue performance code start_on product payment_method delivery_method last_name first_name last_name_kana first_name_kana zip country prefecture city address1 address2 tel1 tel2 fax mail1 mail2 sex birthday memo last_name2 first_name2 last_name2_kana first_name2_kana nickname profile_sex profile_birthday channel browserid membership_name membergroup_name membergroup_id nikoniko_id')




-    普通の抽選
-    10958, 10959, 10963, 10964, 10965
LotData = namedtuple('LotData',
    'status entry_no wish created_at stock_type quantity event venue performance code start_on product payment_method delivery_method last_name first_name last_name_kana first_name_kana zip country prefecture city address1 address2 tel1 tel2 fax mail1 mail2 sex birthday memo last_name2 first_name2 last_name2_kana first_name2_kana nickname profile_sex profile_birthday channel browserid membership_name membergroup_name membergroup_id')


"""
LotData = namedtuple('LotData',
    'status entry_no wish created_at stock_type quantity event venue performance code start_on product payment_method delivery_method last_name first_name last_name_kana first_name_kana zip country prefecture city address1 address2 tel1 tel2 fax mail1 mail2 sex birthday memo last_name2 first_name2 last_name2_kana first_name2_kana nickname profile_sex profile_birthday channel browserid membership_name membergroup_name membergroup_id')


def except_duplicate(argv, row, wrong_writer, result_file_name):
    if not except_duplicate_address(argv, row, wrong_writer, result_file_name):
        return False
    if not except_duplicate_tel(argv, row, wrong_writer, result_file_name):
        return False
    if not except_duplicate_mail(argv, row, wrong_writer, result_file_name):
        return False
    if not except_duplicate_wrongname(argv, row, wrong_writer, result_file_name):
        return False
    return True


def format_address(city, address1, address2):
    # チョップ、丁目、番地、番、ハイフン、文字化け
    address = "{0}{1}{2}".format(city.strip(), address1.strip(), address2.strip())
    address = address.replace("ー", "-")
    address = address.replace("?", "-")
    address = address.replace("丁目", "-")
    address = address.replace("番", "")
    address = address.replace("番地", "")
    address = address.replace("号", "")
    return address


def except_duplicate_address(argv, target_row, wrong_writer, result_file_name):
    # 住所
    target_address = format_address(target_row.city, target_row.address1, target_row.address2)
    with open(result_file_name, 'r') as f:
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


def format_tel(tel):
    # チョップ、ハイフン
    tel = "{0}".format(tel.strip())
    tel = tel.replace("ー", "")
    tel = tel.replace("-", "")
    return tel


def except_duplicate_tel(argv, target_row, wrong_writer, result_file_name):
    # 電話
    target_tel = format_tel(target_row.tel1)
    with open(result_file_name, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)

        for row in reader:
            lot_data = LotData._make(row)
            tel = format_tel(lot_data.tel1)
            if tel == target_tel:
                tel_writer = wrong_writer['tel']
                tel_writer.writerow(target_row)
                return False
    return True


def format_mail(mail):
    # チョップ、大文字小文字
    mail = "{0}".format(mail.strip())
    mail = mail.lower()
    return mail


def except_duplicate_mail(argv, target_row, wrong_writer, result_file_name):
    # メアド
    target_mail = format_mail(target_row.mail1)
    with open(result_file_name, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)

        for row in reader:
            lot_data = LotData._make(row)
            mail = format_mail(lot_data.mail1)
            if mail == target_mail:
                mail_writer = wrong_writer['mail']
                mail_writer.writerow(target_row)
                return False
    return True


def format_name(last_name, first_name):
    # チョップ
    name = "{0}{1}".format(last_name.strip(), first_name.strip())
    return name


def except_duplicate_wrongname(argv, target_row, wrong_writer, result_file_name):
    # 同姓同名
    target_name = format_name(target_row.last_name, target_row.first_name)
    with open(result_file_name, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)

        for row in reader:
            lot_data = LotData._make(row)
            name = format_name(lot_data.last_name, lot_data.first_name)
            if name == target_name:
                wrong_name_writer = wrong_writer['wrongname']
                wrong_name_writer.writerow(target_row)
                return False
    return True


def create_writer(argv, name):
    file_name = "{0}{2}_{1}_{3}.csv".format(argv[2], argv[0], argv[1], name)
    if os.path.isfile(file_name):
        os.remove(file_name)
    csv_file = open(file_name, 'w')
    writer = csv.writer(csv_file)
    return file_name, csv_file, writer


def create_apped_file(argv, file_name):
    csv_file = open(file_name, 'a')
    writer = csv.writer(csv_file)
    return csv_file, writer


def main(argv=sys.argv[1:]):
    # 抽選申込リストを読み込んで重複をなくすスクリプト
    # 引数：prefix(抽選名称など1回目、2回目など), 抽選番号, フォルダパス, 入力ファイル名
    input_file = "{0}{1}".format(argv[2], argv[3]) # 入力ファイル

    # 入力ファイルをエクセルで読めるSJIS -> UTF8へ変換
    os.system('nkf -w --overwrite {0}'.format(input_file))

    result_file_name = "{0}{2}_{1}_result.csv".format(argv[2], argv[0], argv[1])
    address_file_name, address_csv, address_wrong_writer = create_writer(argv, "address")
    tel_file_name, tel_csv, tel_wrong_writer = create_writer(argv, "tel")
    mail_file_name, mail_csv, mail_wrong_writer = create_writer(argv, "mail")
    wrongnmae_file_name, wrongnmae_csv, wrongnmae_wrong_writer = create_writer(argv, "wrongname")

    if os.path.isfile(result_file_name):
        os.remove(result_file_name)

    csv_list = [address_csv, tel_csv, mail_csv, wrongnmae_csv]
    file_name_list = [input_file, result_file_name, address_file_name, tel_file_name, mail_file_name, wrongnmae_file_name]
    wrong_writer_dict = {'address': address_wrong_writer, 'tel': tel_wrong_writer, 'mail': mail_wrong_writer, 'wrongname': wrongnmae_wrong_writer}

    print "start except duplicate script"
    with open(input_file, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)

        # header書き込み
        result_csv, result_writer = create_apped_file(argv, result_file_name)
        result_writer.writerow(header)
        result_csv.close()

        for row in reader:
            lot_data = LotData._make(row)
            ret = except_duplicate(argv, lot_data, wrong_writer_dict, result_file_name)

            if ret:
                # 結果が全てTrueの場合書き出し
                result_csv, result_writer = create_apped_file(argv, result_file_name)
                result_writer.writerow(row)
                result_csv.close()

    for csv_file in csv_list:
        csv_file.close()

    # 作成したファイルをUTF8 -> エクセルで読めるSJISに変換
    for file_name in file_name_list:
        os.system('nkf -s --overwrite {0}'.format(file_name))

    print "end except duplicate script"


if __name__ == '__main__':
    main()
