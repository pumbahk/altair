# coding: utf-8
# -*- coding:utf-8 -*-
from datetime import datetime, timedelta


def create_make_file():
    # Makefile用標準出力する
    # 使用するときは、Makefileをバッチサーバの/home/ticketstar/に作成し、sudo -u ticketstar make

    from_datetime = datetime.strptime('2016-12-01', '%Y-%m-%d')
    to_datetime = datetime.now()

    disp_format = "time /srv/altair/current/deploy/production/bin/send_spdb -c /srv/altair/current/deploy/production/conf/altair.ticketing.batch.ini -o {0} -f {1} -t {2} {3}"
    orgs = [4, 15, 24]

    display(orgs, from_datetime, to_datetime, disp_format, False)
    display(orgs, from_datetime, to_datetime, disp_format, True)


def display(orgs, from_datetime, to_datetime, disp_format, delete_flag):
    for org in orgs:
        from_time = from_datetime
        to_time = from_datetime + timedelta(days=1)
        while to_time < to_datetime:
            if delete_flag:
                print "{0} - {1} {2} {3}".format(from_time.strftime("%Y/%m/%d"), to_time.strftime("%Y/%m/%d"), org, "delete")
                print(disp_format.format(org, from_time.strftime("%Y/%m/%d"), to_time.strftime("%Y/%m/%d"), "-d true"))
            else:
                print "{0} - {1} {2} {3}".format(from_time.strftime("%Y/%m/%d"), to_time.strftime("%Y/%m/%d"), org, "update")
                print(disp_format.format(org, from_time.strftime("%Y/%m/%d"), to_time.strftime("%Y/%m/%d"), ""))
            from_time = from_time + timedelta(days=1)
            to_time = to_time + timedelta(days=1)


if __name__ == '__main__':
    create_make_file()
