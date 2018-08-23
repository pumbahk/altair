#! /usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import subprocess
import sys
from filecmp import dircmp

# 重複を持つファイルのパス
TARGET_PATHS = [
    'cart' + os.sep + 'templates',
    'cart' + os.sep + 'static',
    'lots' + os.sep + 'templates',
    'lots' + os.sep + 'static',
    'orderreview' + os.sep + 'templates',
    'orderreview' + os.sep + 'static',
    'fc_auth' + os.sep + 'static',
]

# meldではなくファイルを開いて確認を行うべきファイルの拡張子
HARD_TO_COMPARE_BY_MELD_EXT = ['.tif', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.pict']

# 文字装飾
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'


def main():
    """
    過去のORG追加作業で不要に増加した重複ファイルを削除。

    スクリプトが信用できない場合を考慮し、削除前に目視で対象を確認可能です（画像ファイルのみ）。
    各自のPCの画像ファイルを開くためのデフォルトアプリが起動します。

    自動削除の実行後、TARGET_PATHSで定義したディレクトリを差分ツール「meld」で比較します。
    インストールされていない場合は、brew install meldやapt-get install meldなどでどうぞ。
    半角スペースの入っている数が違うなどの細かな差分はここで人間の目で見て解決してください。

    :return: void
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_org', metavar='dir_org', type=str)  # 対象とするORG
    parser.add_argument('--dir_base', metavar='dir_base', type=str, default='__base__')  # 比較元とするディレクトリ
    parser.add_argument('--img_confirm', action='store_true')  # 削除前の確認の有無
    parser.add_argument('--report_only', action='store_true')  # 削除は行わず差分の確認だけ出力
    args = parser.parse_args()

    ticketing_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    for target in TARGET_PATHS:
        target_path = ticketing_dir + os.sep + target

        dcmp = dircmp(target_path + os.sep + args.dir_base, target_path + os.sep + args.dir_org)
        try:
            print(dcmp.report_full_closure())
        except OSError:
            print(WARNING + 'Could not find "{}" in "{}"'.format(args.dir_org, target_path) + ENDC)
            continue

        if args.report_only:
            print(HEADER + '------- you chosen only report. so, good bye for now ------' + ENDC)
            return exit(0)

        # 削除の実行
        remove_same_files(dcmp, args)

        # 仕上げにmeldで比較
        print(HEADER + '------- meld will be opened -------' + ENDC)
        subprocess.call(['meld', dcmp.left, dcmp.right])

    print(HEADER + '------- process has finished ------' + ENDC)
    return exit(0)


def remove_same_files(dcmp, args):
    for name in dcmp.right_list:
        # ORGディレクトリ化でシムリンクを貼ってある場合はunlink
        org_file_path = dcmp.right + os.sep + name
        if os.path.islink(org_file_path):
            print(OKBLUE + 'Found symbolic link and deleted: {}'.format(org_file_path) + ENDC)
            os.unlink(org_file_path)

    for name in dcmp.same_files:
        print('Same files {} found in {} and {}'.format(name, dcmp.left, dcmp.right))
        base_file_path = dcmp.left + os.sep + name
        org_file_path = dcmp.right + os.sep + name

        # ファイルでなければスキップ
        if not os.path.isfile(org_file_path):
            print(FAIL + 'Not a file. Can not delete: {}'.format(dcmp.right) + ENDC)
            continue

        # 画像削除前の確認オプション（--img_confirm）が指定されていた場合
        if args.img_confirm:
            _, ext = os.path.splitext(name)
            if ext in HARD_TO_COMPARE_BY_MELD_EXT:
                subprocess.call(['open', '-g', base_file_path, org_file_path])

            ans = raw_input("Are you sure to delete? then, type 'y': ")
            if ans != 'y':
                continue

        print(OKGREEN + 'Deleted -> {}: {}'.format(args.dir_org, org_file_path) + ENDC)
        os.remove(org_file_path)

    # サブディレクトリがある場合は再帰的に実行していく
    for sub_dcmp in dcmp.subdirs.values():
        remove_same_files(sub_dcmp, args)

if __name__ == '__main__':
    sys.exit(main())
