# -*- coding: utf-8 -*-
import argparse

before_type = None
before_where = None
last_select = None


def main():
    parser = argparse.ArgumentParser(description='SQL Check')
    parser.add_argument('file')
    args = parser.parse_args()
    check_sql(args.file)


def check_sql(file):
    try:
        f = open(file)
    except IOError as e:
        print(u"ファイルが見つかりません。path={0}".format(file))
        return

    cnt = 0
    status = list()
    data = f.read()
    data = data.lower()
    data = data.replace('\n', '')
    data = data.replace('\r', '')
    data = data.replace('\g', ';')

    for actual_cnt, line in enumerate(data.split(";")):
        # 空行は読み飛ばす
        line = line.strip()
        if not line:
            continue

        cnt += 1

        if cnt == 1:
            status.append(check_first_line(line))
            continue

        status.append(check_line(actual_cnt, line))

    # 最終行はSELECT文でないとならない
    if before_type != "select":
        print(u"最後はSELECT文で、確認してください。もしくは、サンドイッチされていません。")
        status.append(False)

    if cnt < 4:
        print(u"最低でもBEGINと、SELECT文２つと、更新系のSQLで、４行必要です。")
        status.append(False)

    if all(status):
        print(u"全てのチェックに通りました")


def check_first_line(line):
    status = True
    if line != "begin":
        print(u"1行目には、BEGIN;を指定してください")
        status = False
    return status


def check_line(actual_cnt, line):
    status = True
    if line.startswith("begin"):
        status = check_begin(actual_cnt, line)
    elif line.startswith("select"):
        status = check_select(actual_cnt, line)
    elif line.startswith("update"):
        status = check_update(actual_cnt, line)
    elif line.startswith("delete"):
        status = check_delete(actual_cnt, line)
    return status


def check_begin(actual_cnt, line):
    global before_where
    global before_type
    global last_select

    print(u"{0}行目余計なBEGINがあります。".format(actual_cnt))
    status = False

    before_type = "begin"
    return status


def check_select(actual_cnt, line):
    global before_where
    global before_type
    global last_select
    status = True

    if not line.count("where"):
        print(u"{0}行目のSELECT文にWHERE句がありません。".format(actual_cnt))
        status = False

    where_point = line.find("where")

    if last_select:
        # 更新後のSQLの場合
        if before_where:
            if not before_where == line[where_point:]:
                print(u"{0}行目のSELECT文が、WHERE句が一致しません。".format(actual_cnt))
                status = False

        if line != last_select:
            print(u"{0}行目のSELECT文が、前回のSELECT文と一致しません。サンドイッチしてください。".format(actual_cnt))
            status = False
        last_select = None
    else:
        # 更新前のSQLを保存
        last_select = line

    before_where = line[where_point:]
    before_type = "select"
    return status


def check_update(actual_cnt, line):
    global before_where
    global before_type
    global last_select
    status = True

    if not line.count("where"):
        print(u"{0}行目のUPDATE文にWHERE句がありません。".format(actual_cnt))
        status = False

    where_point = line.find("where")

    if before_type != "select":
        print(u"{0}行目のUPDATE文の前に、SELECT文がありません。".format(actual_cnt))
        status = False

    if before_where:
        if not before_where == line[where_point:]:
            print(u"{0}行目のUPDATE文が、前の行のWHERE句と一致しません".format(actual_cnt))
            status = False

    before_where = line[where_point:]
    before_type = "update"
    return status


def check_delete(actual_cnt, line):
    global before_where
    global before_type
    global last_select
    status = True

    if not line.count("where"):
        print(u"{0}行目のDELETE文にWHERE句がありません。".format(actual_cnt))
        status = False

    where_point = line.find("where")

    if before_type != "select":
        print(u"{0}行目のDELETE文の前に、SELECT文がありません。".format(actual_cnt))
        status = False

    if before_where:
        if not before_where == line[where_point:]:
            print(u"{0}行目のDELETE文が、前の行のWHERE句と一致しません".format(actual_cnt))
            status = False

    before_where = line[where_point:]
    before_type = "delete"
    return status

if __name__ == '__main__':
    main()
