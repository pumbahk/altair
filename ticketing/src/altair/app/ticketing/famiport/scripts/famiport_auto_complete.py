# -*- coding: utf-8 -*-
"""90分自動確定処理

- 申込を行いPOSで入金を行わず30分VOID処理も行われない場合はプレイガイド側で90分自動確定処理を行う
- 確定したものはメールを送信する

メールアドレスは次の順序で取得する
----------------------------------

1. コマンドラインパラメータ
2. 設定ファイル

設定されていなければエラー終了する。

"""
import sys
import logging
import argparse
from pyramid.paster import bootstrap, setup_logging
from altair.multilock import (
    MultiStartLock,
    AlreadyStartUpError,
    )
from altair.sqlahelper import get_global_db_session
from altair.timeparse import parse_time_spec
from altair.app.ticketing.famiport.interfaces import IFamiPortOrderAutoCompleter
from altair.app.ticketing.famiport.autocomplete import (
    FamiPortOrderAutoCompleter,
    FamiPortOrderAutoCompleteRunner,
    )

_logger = logging.getLogger(__file__)
LOCK_NAME = 'FAMIPORT_AUTO_COMPLETE'  # 多重起動防止用の名前


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--stdout', default=False, action='store_true')
    parser.add_argument('--recipients', default=None)
    parser.add_argument('--no-commit', default=None, action='store_true')
    parser.add_argument('-C', '--config', metavar='config', type=str, dest='config', required=True, help='config file')
    args = parser.parse_args(argv)

    if not args.stdout:
        setup_logging(args.config)

    recipients = None
    if args.recipients:
        recipients = [recipient.strip() for recipient in args.recipients.split(',')]

    env = bootstrap(args.config)
    registry = env['registry']
    session = get_global_db_session(registry, 'famiport')

    completer = FamiPortOrderAutoCompleter(
        registry, no_commit=args.no_commit, recipients=recipients)
    registry.registerUtility(completer, IFamiPortOrderAutoCompleter)

    auto_complete_delta = None
    try:
        auto_complete_time = registry.settings['altair.famiport.auto_complete_time']
        auto_complete_delta = parse_time_spec(auto_complete_time)
    except KeyError as err:
        _logger.exception('invalid auto complete time setting: {}'.format(err))
        return 254
    if auto_complete_delta is None:
        _logger.exception('auto complete time no setting')
        return 253

    completer = FamiPortOrderAutoCompleteRunner(registry, auto_complete_delta)
    _logger.info('famiport auto complete start')
    try:
        with MultiStartLock(LOCK_NAME, engine=session.bind):
            _logger.info('get a multiple lock')
            errors = completer.get_setup_errors()
            if not errors:
                successes, fails = completer.complete_all(session)
                _logger.info(
                    'famiport auto complete finished: success={}, failed={}'.format(
                        successes, fails))
            else:
                _logger.error(errors[0])
                return 255
    except AlreadyStartUpError as err:
        _logger.warn('{}'.format(repr(err)))
    _logger.info('famiport auto complete end')

if __name__ == u"__main__":
    sys.exit(main())
