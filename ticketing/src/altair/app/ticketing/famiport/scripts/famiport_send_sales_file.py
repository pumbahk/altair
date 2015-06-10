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

    sales_file_manager = FamiPortFileManager(registry, FamiPortFileType.SALES)
    staged_file_path = None
    try: # TODO Take care of staged_file_path
        logger.info("sending sales file.")
        staged_file_path = sales_file_manager.send_staged_file(FamiPortFileType.SALES)
        print 'staged_file_path: %s' % staged_file_path
        sales_file_manager.mark_file_sent(staged_file_path)
    except:
        logger.error("failed to send sales file: %s" % staged_file_path)
        sales_file_manager.mark_file_pending(staged_file_path)

    # sales_file_dir = settings['altair.famiport.sales_file.dir']
    # upload_dir_path = settings['altair.famiport.send_file.ftp.upload_dir_path']
    #
    # sales_file_name = 'SAL_DAT.txt'
    # sales_file_path = os.path.join(sales_file_dir, sales_file_name)
    #
    # logger.info('Sending sales file in %s' % sales_file_dir)
    # sender = registry.queryUtility(IFileSender, name='ftps')
    # # TODO Move files from staged to sent
    # if not os.path.exists(sales_file_path):
    #     raise Exception('%s does not exist' % sales_file_path)
    # else:
    #     with open(sales_file_path) as f:
    #         sender.send_file(os.path.join(upload_dir_path, sales_file_name), f)
    #
    # transfer_complete_filename = 'SAL_DAT_FLG.txt' # 転送完了フラグファイル
    # with open (transfer_complete_filename, 'w+') as f:
    #     sender.send_file(os.path.join(upload_dir_path, transfer_complete_filename), f)

if __name__ == u"__main__":
    main(sys.argv)
