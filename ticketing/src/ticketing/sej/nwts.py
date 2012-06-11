# -*- coding: utf-8 -*-

CMD_WINE='/usr/local/bin/wine'
CMD_NWTS='nwtsUL.exe'

SERVER_HOST='incp.r1test.coms'
DIR_NAME='/cpweb/master/ul'

TERMINAL_ID='60022000'
PASSWORD='60022a'

def exec_nwts(server_host, dir_name, terminal_id, password, file_id, file_name, path):
    cmd = "%s %s -s %s -d %s -t %s -p %s -f %s -o %s -e %s %s - " % \
        (CMD_WINE, CMD_NWTS, server_host, dir_name, terminal_id, password, file_id, file_name, path, '-u')
    print cmd

def main():
    exec_nwts('localhost', '/cpweb/master/ul', '60022000', '60022a', 'SEIT020U', 'file', 'tpayback.asp')


if __name__ == '__main__':
    main()
