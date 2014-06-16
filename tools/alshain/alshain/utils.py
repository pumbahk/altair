#-*- coding: utf-8 -*-
import os
import warnings
import subprocess
import ConfigParser
import jumon
from enum import Enum, unique



class DeploymentWarning(UserWarning):
    pass

class ConfigurationError(Exception):
    pass

class DoesNotDefinedRootDirectory(Exception):
    def __str__(self):
        return 'Does not defined root directory path `ALTAIR`. Sould be `export ALTAIR=ALTAIR_ROOT_PATH`'

def get_root_dir():
    try:
        return os.environ['ALTAIR']
    except KeyError:
        raise DoesNotDefinedRootDirectory()

class DeployStyle(Enum):
    develop = 'dev'
    staging = 'staging'
    production = 'production'

class Env(Enum):
    ALTAIR = '/srv/altair/current'
    ALTAIR_DEPLOY = DeployStyle.develop.value
    ALTAIR_SUDO = ''

    @classmethod
    def get(self, env):
        try:
            return os.environ[env.name]
        except KeyError as err:
            return env.value



class PathSelector(object):

    @staticmethod
    def _get_path(path, name=None, ignore_noexist=False):
        if name:
            path = os.path.join(path, name)
        if ignore_noexist or os.path.exists(path):
            return path
        else:
            raise IOError('Not found: {0}'.format(path))

    @property
    def root(self, *args, **kwds):
        try:
            return os.environ[Env.ALTAIR]
        except KeyError:
            raise DoesNotDefinedRootDirectory()
    @property
    def root_dir(self):
        try:
            return os.environ['ALTAIR']
        except KeyError:
            raise DoesNotDefinedRootDirectory()


class DeploySwitcher(object):
    ENVIRONMENT_VARIABLE = 'ALTAIR_DEPLOY'
    DEPLOY_PATH = 'deploy'
    NOW_SUPPORT_DEPLOY = ('dev', 'staging', 'production')

    @classmethod
    def get_name(cls):
        try:
            deploy = os.environ[cls.ENVIRONMENT_VARIABLE]
            if not deploy in cls.NOW_SUPPORT_DEPLOY:
                warnings.warn('Not support Deployment: {0}'.format(deploy),
                              DeploymentWarning)
        except KeyError:
            msg = 'Set the default value, Because the "{0}" environment variable so has not been set.'\
                .format(cls.ENVIRONMENT_VARIABLE)
            warnings.warn(msg, DeploymentWarning)
            deploy = 'dev'
        return deploy

    @classmethod
    def get_dir(cls):
        root = get_root_dir()
        return os.path.join(root, cls.DEPLOY_PATH, cls.get_name())


def get_deploy_dir():
    root = get_root_dir()
    try:
        return os.environ['ALTAIR']
    except KeyError:
        raise DoesNotDefinedRootDirectory()


def get_supervisord_conf():
    root = get_root_dir()
    deploy = DeploySwitcher.get_name()
    return os.path.join(root, 'deploy/{}/parts/supervisor/supervisord.conf'.format(deploy))


def get_command(name):
    path = get_supervisord_conf()
    try:
        conf = ConfigParser.SafeConfigParser()
    except ConfigParser.Error:
        raise

    successes = conf.read(path)
    if not path in successes:
        raise ConfigurationError(path)

    try:
        return conf.get('program:{0}'.format(name), 'command')
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError) as err:
        raise

def call(line, *args, **kwds):
    print
    print '$', line
    if not 'shell' in kwds:
        kwds['shell'] = True
    return subprocess.Popen(line, *args, **kwds)

class Shell(jumon.Shell):

    @classmethod
    def get_sudo_user(cls, sudo=None):
        if sudo is True:
            sudo = Env.get(Env.ALTAIR_SUDO)
        return sudo


class AltairPath(object):
    def __init__(self, root=None, style_name=None):
        self._root = root if root else self.get_root()
        self._style_name = style_name if style_name else self.get_style()

    @classmethod
    def join(self, *args, **kwds):
        return os.path.join(*args, **kwds)

    def get_root(self):
        return Env.get(Env.ALTAIR)

    def get_style(self):
        return Env.get(Env.ALTAIR_DEPLOY)

    def root(self, *args, **kwds):
        return self.join(self._root, *args, **kwds)

    def deploy(self, *args, **kwds):
        return self.root('deploy', *args, **kwds)

    def style(self, *args, **kwds):
        return self.deploy(Env.get(Env.ALTAIR_DEPLOY), *args, **kwds)

    def ticketing(self, *args, **kwds):
        return self.root('ticketing', *args, **kwds)

    def cms(self, *args, **kwds):
        return self.root('cms', *args, **kwds)

    def bin_(self, *args, **kwds):
        return self.style('bin', *args, **kwds)

    def conf(self, *args, **kwds):
        return self.style('conf', *args, **kwds)

    def env(self, *args, **kwds):
        return self.style('env', *args, **kwds)

class AlshainPath(object):
    @classmethod
    def join(self, *args, **kwds):
        return os.path.join(*args, **kwds)

    def scripts(self, *args, **kwds):
        scripts_dir = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)), 'scripts')
        return self.join(scripts_dir, *args, **kwds)
