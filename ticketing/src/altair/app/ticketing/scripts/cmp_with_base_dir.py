#! /usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import os
import sys
import argparse
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


def main():
    """
    過去のORG追加作業で不要に増加した重複ファイルを削除。
    スクリプトが信用できない場合を考慮し、削除前に目視で対象を確認できるようにしています。
    画像ファイルなどは各自のPCの画像ファイルを開くためのデフォルトアプリで起動、それ以外はmeldを利用して比較します。
    インストールされていない場合は、brew install meldやapt-get install meldなどでどうぞ。
    :return: void
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_org', metavar='dir_org', type=str)  # 対象とするORG
    parser.add_argument('--dir_base', metavar='dir_base', type=str, default='__base__')  # 比較元とするディレクトリ
    parser.add_argument('--confirm', action='store_true')  # 削除前の確認の有無
    parser.add_argument('--report_only', action='store_true')  # 削除は行わず差分の確認だけ出力
    args = parser.parse_args()

    ticketing_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    for target in TARGET_PATHS:
        target_path = ticketing_dir + os.sep + target

        dcmp = dircmp(target_path + os.sep + args.dir_base, target_path + os.sep + args.dir_org)
        print(dcmp.report_full_closure())

        if not args.report_only:
            remove_same_files(dcmp, args)


def remove_same_files(dcmp, args):
    for name in dcmp.same_files:
        print('same files {} found in {} and {}'.format(name, dcmp.left, dcmp.right))
        base_file_path = dcmp.left + os.sep + name
        org_file_path = dcmp.right + os.sep + name

        if not os.path.isfile(org_file_path):
            continue

        if args.confirm:
            _, ext = os.path.splitext(name)
            if ext in HARD_TO_COMPARE_BY_MELD_EXT:
                subprocess.call(['open', '-g', base_file_path, org_file_path])
            else:
                subprocess.call(['meld', '-n', base_file_path, org_file_path])

            ans = raw_input("削除して良ければ'y'を押してください: ")
            if ans != 'y':
                continue

        print('{}の{}を削除します。'.format(args.dir_org, org_file_path))
        os.remove(org_file_path)

    for sub_dcmp in dcmp.subdirs.values():
        remove_same_files(sub_dcmp, args)

if __name__ == '__main__':
    sys.exit(main())
