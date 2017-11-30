#-*- coding: utf-8 -*-
#!/usr/bin/env python
import os
import sys
import csv
import pandas as pd
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
    'status entry_no wish created_at stock_type quantity event venue performance code start_on product payment_method delivery_method last_name first_name last_name_kana first_name_kana zip country prefecture city address1 address2 tel1 tel2 fax mail1 mail2 sex birthday memo last_name2 first_name2 last_name2_kana first_name2_kana nickname profile_sex profile_birthday channel browserid membership_name membergroup_name membergroup_id like_artist')


mail_white_list = [
    u'docomo.ne.jp',
    u'mopera.net',
    u'softbank.ne.jp',
    u'vodafone.ne.jp',
    u't.vodafone.ne.jp',
    u'd.vodafone.ne.jp',
    u'h.vodafone.ne.jp',
    u'c.vodafone.ne.jp',
    u'k.vodafone.ne.jp',
    u'r.vodafone.ne.jp',
    u'n.vodafone.ne.jp',
    u's.vodafone.ne.jp',
    u'q.vodafone.ne.jp',
    u'disney.ne.jp',
    u'i.softbank.jp',
    u'ezweb.ne.jp',
    u'biz.ezweb.ne.jp',
    u'augps.ezweb.ne.jp',
    u'ido.ne.jp',
    u'emnet.ne.jp',
    u'emobile.ne.jp',
    u'emobile-s.ne.jp',
    u'pdx.ne.jp',
    u'wm.pdx.ne.jp',
    u'dk.pdx.ne.jp',
    u'di.pdx.ne.jp',
    u'dj.pdx.ne.jp',
    u'willcom.com',
    u'wcm.ne.jp',
    u'disneymobile.ne.jp',
    u'rakuten.jp',
    u'mineo.jp',
    u'ocn.ne.jp',
    u'yahoo.co.jp',
    u'gmail.com',
    u'me.com',
    u'icloud.com',
    u'mac.com'
]


def except_blacklist(argv, row, wrong_writer, result_file_name):
    if not except_age(argv, row, wrong_writer, result_file_name):
        return False
    if not except_blacklist_mail(argv, row, wrong_writer, result_file_name):
        return False
    if not except_wrongname(argv, row, wrong_writer, result_file_name):
        return False
    return True


def format_age(birthday):
    # 年齢に整形する(公演日当時の年齢を出す)
    try:
        birthday = birthday.strip()
        start_on = int(pd.to_datetime('2017/12/31').strftime('%Y%m%d'))
        birth = int(pd.to_datetime(birthday.strip()).strftime('%Y%m%d'))
        age = int((start_on - birth) / 10000)
    except ValueError:
        return None
    return age


def except_age(argv, target_row, wrong_writer, result_file_name):
    # 二部公演の場合、未成年を弾く。おばさんを両公演弾く
    target_age = format_age(target_row.birthday)

    # 不正なデータ
    if not target_age:
        age_writer = wrong_writer['age']
        age_writer.writerow(target_row)
        return False

    # おばさん
    #if target_age >= 40:
    #    age_writer = wrong_writer['age']
    #    age_writer.writerow(target_row)
    #    return False

    # 未成年かつ、二部の公演
    if argv[0] == '2' and target_age < 20:
        age_writer = wrong_writer['age']
        age_writer.writerow(target_row)
        return False
    return True


def format_domain(mail):
    mail = "{0}".format(mail.strip())
    mail = mail.lower()
    index = mail.find('@')
    if index == -1:
        return None
    domain = mail[index+1:]
    return domain


def except_blacklist_mail(argv, target_row, wrong_writer, result_file_name):
    # メールのホワイトリスト以外を弾く
    target_mail = format_domain(target_row.mail1)
    if None:
        # ドメインの体をなしていない
        blackmail_writer = wrong_writer['blackmail']
        blackmail_writer.writerow(target_row)
        return False

    if target_mail not in mail_white_list:
        # ホワイトリスト以外
        blackmail_writer = wrong_writer['blackmail']
        blackmail_writer.writerow(target_row)
        return False

    return True


def format_name(last_name, first_name):
    # チョップ
    name = "{0}{1}".format(last_name.strip(), first_name.strip())
    return name


def except_wrongname(argv, target_row, wrong_writer, result_file_name):
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
    # ブラックリストを読み込んで抽選申し込みから削除するスクリプト
    # 引数：prefix(抽選名称など1回目、2回目など), 抽選番号, フォルダパス, 入力ファイル名
    input_file = "{0}{1}".format(argv[2], argv[3])

    # 入力ファイルをエクセルで読めるSJIS -> UTF8へ変換
    os.system('nkf -w --overwrite {0}'.format(input_file))

    result_file_name = "{0}{2}_{1}_result.csv".format(argv[2], argv[0], argv[1])
    age_file_name, age_csv, age_writer = create_writer(argv, "age")
    blackmail_file_name, blackmail_csv, blackmail_writer = create_writer(argv, "blackmail")
    wrongname_file_name, wrongname_csv, wrongname_writer = create_writer(argv, "wrongname")

    if os.path.isfile(result_file_name):
        os.remove(result_file_name)

    csv_list = [age_csv, blackmail_csv, wrongname_csv]
    file_name_list = [input_file, result_file_name, age_file_name, blackmail_file_name, wrongname_file_name]
    wrong_writer_dict = {'age': age_writer, 'blackmail': blackmail_writer, 'wrongname': wrongname_writer}

    print "start except blacklist script"
    with open(input_file, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)

        # header書き込み
        result_csv, result_writer = create_apped_file(argv, result_file_name)
        result_writer.writerow(header)
        result_csv.close()

        for row in reader:
            lot_data = LotData._make(row)
            ret = except_blacklist(argv, lot_data, wrong_writer_dict, result_file_name)

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

    print "end except blacklist script"


if __name__ == '__main__':
    main()
