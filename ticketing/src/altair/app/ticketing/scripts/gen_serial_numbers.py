import os
import sys
import struct
import argparse
import sqlite3
import tempfile
from altair.app.ticketing.utils import DigitCodec

def message(msg):
    sys.stderr.write("%s: %s\n" % (os.path.basename(sys.argv[0]), msg))
    sys.stderr.flush()

class ApplicationError(Exception):
    pass

class Generator(object):
    def __init__(self, conn, numchars, charset):
        self.conn = conn
        self.numchars = numchars
        self.charset = charset
        self.encoder = DigitCodec(self.charset)
        self.retry_count = 10
        self.setup_tables()

    @classmethod
    def create_from_conn(cls, conn):
        try:
            c = conn.cursor()
            c.execute('SELECT numchars, charset FROM SerialConfig;')
            r = c.fetchone()
            if r is not None:
                return cls(
                    conn,
                    numchars=r[0],
                    charset=r[1]
                    )
        except sqlite3.OperationalError:
            pass
        return None

    @property
    def existing_serial_count(self):
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM Serial;")
        row = c.fetchone()
        return row[0]

    def setup_tables(self):
        try:
            c = self.conn.cursor()
            c.execute("CREATE TABLE SerialConfig (numchars INTEGER NOT NULL, charset VARCHAR(255) NOT NULL);")
            self.conn.commit()
        except sqlite3.OperationalError:
            pass  
        try:
            c = self.conn.cursor()
            c.execute("CREATE TABLE Serial (serial VARCHAR(255) NOT NULL, PRIMARY KEY (serial));")
            self.conn.commit()
        except sqlite3.OperationalError:
            pass  

    def save_config(self):
        try:
            c = self.conn.cursor()
            c.execute("DELETE FROM SerialConfig;")
            c = self.conn.cursor()
            c.execute("INSERT INTO SerialConfig (numchars, charset) VALUES (?, ?);", (self.numchars, self.charset))
            self.conn.commit()
        except:
            self.conn.rollback()
            raise

    def generate(self):
        try:
            for _ in range(self.retry_count):
                a = struct.unpack('>Q', os.urandom(8))[0]
                v = a % (len(self.charset) ** self.numchars)
                serial = self.encoder.encode(v).zfill(self.numchars)
                try:
                    c = self.conn.cursor()
                    c.execute('INSERT INTO Serial (serial) VALUES (?);', (serial, ))
                    self.conn.commit()
                    break
                except sqlite3.IntegrityError:
                    pass
            else:
                raise ApplicationError('failed to generate a new serial number (%s)' % serial) 
        except:
            self.conn.rollback()
            raise
        return serial


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument('--charset', dest='charset', default='0123456789ACFGHJKLPRSUWXY')
    p.add_argument('--numchars', dest='numchars', type=int)
    p.add_argument('database')
    p.add_argument('count', type=int)

    args = p.parse_args(argv[1:])

    conn = sqlite3.connect(args.database)
    try:
        app = Generator.create_from_conn(conn)
        if app is None:
            if args.numchars is None:
                raise ApplicationError('--numchars must be specified')
            app = Generator(conn, numchars=args.numchars, charset=args.charset)
            app.save_config()
        else:
            if app.numchars != args.numchars:
                raise ApplicationError('specified numchars (%d) is different from that of the existing configuration (%d)' % (args.numchars, app.numchars))
            if app.charset != args.charset:
                raise ApplicationError('specified charset (%s) is different from that of the existing configuration (%s)' % (args.charset, app.charset))
        message('%d serial numbers have been generated so far' % app.existing_serial_count)
        i = 0
        while i < args.count:
            sys.stdout.write("%s\n" % app.generate())
            i += 1
    except ApplicationError as e:
        message(e.message)

if __name__ == '__main__':
    main(sys.argv)
