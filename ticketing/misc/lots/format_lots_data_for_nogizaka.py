# -*- coding:utf-8 -*-
import csv
import sys


def main(argv=sys.argv):
    result_file = open("{0}_result.csv".format(argv[1]), 'w')
    writer = csv.writer(result_file, lineterminator='\n')
    out_header = ['同行者・姓', '同行者名・名', '同行者電話番号(半角・ハイフン不要)', '最終確認', '申込時の注意事項', '申込者乃木坂46モバイル会員登録メールアドレス',
            '申込者乃木坂46モバイル会員登録端末電話番号(半角・ハイフン不要)', '申込者名・名', '申込者名・姓(来場代表者苗字)']
    writer.writerow(out_header)

    position = 0
    with open("{0}.csv".format(argv[1]), 'r') as f:
        reader = csv.reader(f)
        header = next(reader)

        order_list = list()
        for row in reader:
            position += 1
            order_list.append(row)

            if position == 9:
                out_list = order_list[0]
                del out_list[44]
                del out_list[45]
                out_list.append(order_list[1][45])
                out_list.append(order_list[2][45])
                out_list.append(order_list[3][45])
                out_list.append(order_list[4][45])
                out_list.append(order_list[5][45])
                out_list.append(order_list[6][45])
                out_list.append(order_list[7][45])
                out_list.append(order_list[8][45])
                writer.writerow(out_list)

                position = 0
                order_list = list()

    result_file.close()


if __name__ == "__main__":
    main()
