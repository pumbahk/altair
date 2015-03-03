# -*- coding: utf-8 -*-
import os
import optparse
import subprocess

from .. import utils

__all__ = ['main']


class NotSupportVerifyerType(ValueError):
    pass


class Deploy:
    PRODUCTION = 'production'
    STAGING = 'staging'
    DEV = 'dev'


class BaseVerifyer(object):
    NAME = 'virtual'
    workdir = ''
    buildout_conf = ''
    testcmd = ''

    def __init__(self, deploy=Deploy.DEV):
        self.deploy = deploy

    @staticmethod
    def _call(line, *args, **kwds):
        print
        print '$', line
        return subprocess.Popen(line, shell=True, *args, **kwds)

    def verify(self, build=False, nocapture=False):
        self.workon()
        if build:
            child = self.bootstrap()
            child.wait()

            child = self.buildout()
            child.wait()

        child = self.runtest(nocapture)
        child.wait()

    def bootstrap(self):
        child = self._call('python bootstrap.py')
        return child

    def buildout(self):
        cmd = 'bin/buildout'
        conf = self.buildout_conf
        if conf:
            cmd += ' -c {0}'.format(conf)
        child = self._call(cmd)
        return child

    def runtest(self, nocapture=False):
        cmd = self.testcmd
        if nocapture:
            cmd += ' -s'
        child = self._call(cmd)
        return child

    @property
    def root(self):
        if not hasattr(self, '_rootdir'):
            self._rootdir = utils.get_root_dir()
        return self._rootdir

    def chroot(self):
        os.chdir(self.root)

    def workon(self):
        self.chroot()
        path = os.path.join(self.root, self.workdir)
        os.chdir(path)


class TicketingVerifyer(BaseVerifyer):
    """The verifyer implementation of altair.app.ticketing module
    """
    NAME = 'ticketing'
    _workdir = 'deploy'
    buildout_conf = 'buildout.local.cfg'
    testcmd = 'bin/test-ticketing'

    @property
    def workdir(self):
        return os.path.join(self._workdir, self.deploy)


class AltairlibVerifyer(BaseVerifyer):
    """The verifyer implementation of altairlib modules
    """
    NAME = 'altairlib'
    workdir = 'altairlib'
    buildout_conf = None
    testcmd = 'bin/test'


class CMSVerifyer(TicketingVerifyer):
    """The verifyer implementation of altair.cms module
    """
    NAME = 'cms'
    testcmd = 'bin/test-cms'


class Verifyer(object):
    """The verifyer factory.
    """

    verifyers = [TicketingVerifyer,
                 AltairlibVerifyer,
                 CMSVerifyer,
                 ]

    def __new__(cls, name, *args, **kwds):
        for verifyer in cls.verifyers:
            if verifyer.NAME == name:
                return verifyer(*args, **kwds)
        raise NotSupportVerifyerType('Not supported Verifyer type: {0}'.format(name))

    @classmethod
    def names(self, names=[]):
        my_names = [name for name in self.generate_name()]
        return_names = set()

        if not names:
            names = ['all']
        for name in names:
            if name == 'all':
                return_names.update(my_names)
            elif name in my_names:
                return_names.add(name)
            else:
                print 'skip: {0}'.format(name)
        return return_names

    @classmethod
    def generate_name(cls):
        for verifyer in cls.verifyers:
            yield verifyer.NAME


def main(argv):
    parser = optparse.OptionParser()
    parser.add_option('-b', '--build', default=False, action='store_true',
                      help='build environments bootstrap, buildout.')
    parser.add_option('-s', '--nocapture', default=False, action='store_true',
                      help="Don't capture stdout (any stdout output will be printed immediately) [NOSE_NOCAPTURE]")
    opts, args = parser.parse_args(argv)

    for name in Verifyer.names(args):
        verifyer = Verifyer(name)
        verifyer.verify(build=opts.build, nocapture=opts.nocapture)
