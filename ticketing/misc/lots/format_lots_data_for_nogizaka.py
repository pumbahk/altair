# -*- coding:utf-8 -*-
import csv
import sys


def main(argv=sys.argv):
    add_header = map(lambda name: name.encode('sjis'), [
        u"同行者・姓",
        u"同行者名・名",
        u"同行者電話番号(半角・ハイフン不要)",
        u"最終確認",
        u"申込時の注意事項",
        u"申込者乃木坂46モバイル会員登録メールアドレス",
        u"申込者乃木坂46モバイル会員登録端末電話番号(半角・ハイフン不要)",
        u"申込者名・名",
        u"申込者名・姓(来場代表者苗字)",
    ])

    result_file = open("{0}_result.csv".format(argv[1]), 'w')
    writer = csv.writer(result_file, lineterminator='\n')

    with open("{0}.csv".format(argv[1]), 'r') as f:
        reader = csv.reader(f)
        order_list = list()
        first_row = None
        keep_order_no = None

        for row in reader:
            # ヘッダー行作成
            if first_row is None:
                first_row = row + add_header
                writer.writerow(first_row)
                continue

            if keep_order_no is None:
                keep_order_no = row[1]

            # 次の申し込み番号に切り替わった時点で追加情報を収集
            if keep_order_no != row[1]:
                write_formatted_content(writer, order_list)

                # ループ内変数のリセット
                order_list = list()
                keep_order_no = None

            # order_listに取得した行の情報をストック
            order_list.append(row)

    # ファイル末尾の購入情報のフォーマットと書き込み
    write_formatted_content(writer, order_list)

    result_file.close()


def write_formatted_content(writer, order_list):
    '''9行に別れた追加情報を先頭行の予約にまとめて付加する'''
    out_list = order_list[0]
    del out_list[44]
    del out_list[45]
    for i in range(1, 9):
        out_list.append(order_list[i][45])

    writer.writerow(out_list)


if __name__ == "__main__":
    main()
