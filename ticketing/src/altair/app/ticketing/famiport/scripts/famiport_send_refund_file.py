# -*- coding:utf-8 -*-

import argparse
import sys
import os
import logging
from pyramid.paster import bootstrap, setup_logging
from altair.app.ticketing.famiport.datainterchange.interfaces import IFileSender
from ..datainterchange.filetransfer import FamiPortFileManager, FamiPortFileType

logger = logging.getLogger(__name__)

def main(argv=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-C', '--config')
    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)
    registry = env['registry']
    settings = registry.settings

    refund_file_manager = FamiPortFileManager(registry, FamiPortFileType.REFUND)
    staged_file_path = None
    try: # TODO Take care of staged_file_path
        logger.info("sending refund file.")
        staged_file_path = refund_file_manager.send_staged_file(FamiPortFileType.REFUND)
        refund_file_manager.mark_file_sent(staged_file_path)
    except:
        logger.error("failed to send refund file: %s" % staged_file_path)
        refund_file_manager.mark_file_pending(staged_file_path)


    # refund_file_dir = settings['altair.famiport.refund_file.dir']
    # upload_dir_path = settings['altair.famiport.send_file.ftp.upload_dir_path']
    #
    # refund_file_name = 'REF_DAT.txt'
    # refund_file_path = os.path.join(refund_file_dir, refund_file_name)
    #
    # logger.info('Sending refund file in %s' % refund_file_dir)
    # sender = registry.queryUtility(IFileSender, name='ftps')
    # # TODO move files from staged to sent
    # if not os.path.exists(refund_file_path):
    #     raise Exception('%s does not exist' % refund_file_path)
    # else:
    #     with open(refund_file_path) as f:
    #         sender.send_file(os.path.join(upload_dir_path, refund_file_name), f)
    #
    # transfer_complete_filename = 'REF_DAT_FLG.txt' # 転送完了フラグファイル
    # with open (transfer_complete_filename, 'w+') as f:
    #     sender.send_file(os.path.join(upload_dir_path, transfer_complete_filename), f)

if __name__ == u"__main__":
    main(sys.argv)
