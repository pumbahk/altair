# -*- coding:utf-8 -*-
import argparse
import logging
import sys
from datetime import date, timedelta

from altair.app.ticketing.famiport.datainterchange.fileio import MarshalErrorBase
from altair.app.ticketing.famiport.datainterchange.importing import ImportSession, normal_file_filter
from altair.app.ticketing.famiport.mdm.shop_code_change import shop_code_change_schema, shop_code_change_translation
from altair.app.ticketing.famiport.mdm.utils import make_unmarshaller
from altair.app.ticketing.famiport.models import FamiPortReceipt
from altair.sqlahelper import get_global_db_session
from pyramid.paster import setup_logging, bootstrap
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

logger = logging.getLogger(__name__)


class ShopCodeChangeProcessor(object):
    def __init__(self, filename, encoding, db_session):
        self.filename = filename
        self.encoding = encoding
        self.db_session = db_session

    def __call__(self, path):
        """
        ファミマから送られた店番変換リストを読み込み、
        管理番号で一致する 90 分確定のオーダーの店番(仮番号 -> 実番号) と処理日時を更新します。
        """
        if path.endswith(self.filename):
            logger.info(u'Imported %s...', path)

            unmarshaller_error = [None]
            errors = []

            def handle_exception(exc_info):
                if issubclass(exc_info[0], MarshalErrorBase):
                    unmarshaller_error[0] = exc_info[1]
                    errors.append(exc_info[1])
                else:
                    # csv 読込で通常 raise される MarshallError 系でないエラーは処理を中断します。
                    # True を返し, fileio#RecordUnmarshaller 内で raise させます。
                    return True

            try:
                with open(path) as f:
                    unmarshaller = make_unmarshaller(f, shop_code_change_schema,
                                                     encoding=self.encoding, exc_handler=handle_exception)
                    while True:
                        unmarshaller_error[0] = None
                        try:
                            row = unmarshaller.next()
                        except StopIteration:
                            break

                        if unmarshaller_error[0]:
                            continue

                        logger.info(u'Importing line (%s)', translate_row(row))
                        management_number = row['management_number']
                        try:
                            # 管理番号から対象オーダーのレシート情報を探します。
                            # 管理番号は famiport_order_identifier の下9桁と一致します。
                            # famiport_order_identifier の最初3桁は FamiPortClient の prefix です。
                            # 後方一致はインデックスが効かないので、インデックスのある completed_at で過去１週間のデータに絞ってから検索します。
                            # 90 分確定かどうかの判定は完了時刻と救済時刻の有無です。
                            from_day = date.today() - timedelta(days=7)
                            famiport_receipt = self.db_session.query(FamiPortReceipt)\
                                .filter(FamiPortReceipt.completed_at >= from_day.strftime('%Y-%m-%d'))\
                                .filter(FamiPortReceipt.rescued_at.isnot(None))\
                                .filter(FamiPortReceipt.famiport_order_identifier.endswith(management_number))\
                                .one()
                            # 店舗番号の更新。2019年2月現在、元データは7桁ですが先頭2桁は0で埋められているので実質5桁です。
                            # 5桁になるように0でパディングします。
                            # 6桁に突入する際には以下の5桁と対応するテーブルの定義も修正する必要があります。
                            stripped_code = row['shop_code'].lstrip('0')
                            famiport_receipt.shop_code = stripped_code.rjust(5, '0')
                            # 完了時刻も更新します。row['valid'] が False (赤) のときはキャンセルを意味するので、キャンセル処理が必要になるかもしれません。
                            famiport_receipt.completed_at = row['processed_at']

                        except NoResultFound:
                            errors.append(u'management number (={}) not found\n'.format(management_number))
                        except MultipleResultsFound:
                            errors.append(u'management number (={}) found in multiple rows\n'.format(management_number))

                    self.db_session.commit()

                f.close()
                logger.info(u'Done processing %s', path)
            except Exception as exc:
                self.db_session.rollback()
                logger.error(u'[FMB0001] failed to change famima shop code: %s', exc)
                raise exc
            finally:
                if errors:
                    logger.error(u'[FMB0002] Error (path: %s) has occurred:\n%s', path, '\n'.join(errors))
        else:
            # pending ディレクトリにファイルがない、もしくは違う名前のファイルがある場合はエラー出力する
            logger.error(u'[FMB0003] There is no file to import (path: %s)', path)
        return None


class EnvSetup(object):
    def __call__(self, config_uri):
        setup_logging(config_uri)
        env = bootstrap(config_uri)
        return env


def translate_row(row):
    res = [shop_code_change_translation[k] + ': ' + str(v) for k, v in row.items()]
    return ', '.join(res)


def main(argv=sys.argv):
    """
    ファミマから送られてくる店番変換リストを読み込み、仮店番と処理日時を更新します。
    電子バーコード発行で、90分確定となったオーダーが対象です。
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-C', '--config', metavar='config', type=str, dest='config', required=True, help='config file')
    args = parser.parse_args(argv[1:])

    env_setup = EnvSetup()
    env = env_setup(args.config)
    registry = env['registry']
    settings = registry.settings
    pending_dir = settings['altair.famiport.mdm.shop_code_change.pending_dir']
    imported_dir = settings['altair.famiport.mdm.shop_code_change.imported_dir']
    filename = settings['altair.famiport.mdm.shop_code_change.filename']
    encoding = settings.get('altair.famiport.mdm.shop_code_change.encoding', 'CP932')
    db_session = get_global_db_session(registry, 'famiport')

    session = ImportSession(
        pending_dir=pending_dir,
        imported_dir=imported_dir,
        file_filter=normal_file_filter,
        processor=ShopCodeChangeProcessor(filename, encoding, db_session),
        logger=logger
    )
    session()


if __name__ == u"__main__":
    main(sys.argv)
