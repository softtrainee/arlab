from __future__ import with_statement
#============= enthought library imports =======================
#============= standard library imports ========================
import os
import ConfigParser

#============= local library imports  ==========================
from src.helpers import paths
from loggable import Loggable

class ConfigLoadable(Loggable):
    '''
        G{classtree}
    '''
    configuration_dir_name = None
    configuration_dir_path = None
    name = None
    config_path = None



    def bootstrap(self, *args, **kw):
        '''
        '''
        self.info('load')
        if self.load(*args, **kw):
            self.info('open')
            if self.open(*args, **kw):
                self.info('initialize')
                self.initialize(*args, **kw)
                return True
            else:
                self.warning('failed opening')
        else:
            self.warning('failed loading')
    def configparser_factory(self):
        return ConfigParser.ConfigParser()

    def config_get_options(self, config, section):
        r = []
        if config.has_section(section):
            r = config.options(section)
        return r

    def config_get(self, config, section, option, cast = None, optional = False, default = None):
        '''
        '''
        if cast is not None:
            func = getattr(config, 'get%s' % cast)
        else:
            func = config.get

        if not config.has_option(section, option):
            if not optional:
                if self.logger is not None:
                    self.warning('Need to specifiy {}:{}'.format(section, option))

            return default
        else:
            return func(section, option)

    def set_attribute(self, config, attribute, section, option, cast = None, optional = False):
        '''
        '''
        r = self.config_get(config, section, option, cast = cast, optional = optional)

        if r is not None:
            setattr(self, attribute, r)

    def open(self, *args, **kw):
        '''
        '''
        return True

    def load(self, *args, **kw):
        '''

        '''
        return True

    def initialize(self, *args, **kw):
        '''
        '''
        return True

    def write_configuration(self, config, path = None):
        '''

        '''
        if path is None:
            path = self.config_path

        with open(path, 'w') as f:
            config.write(f)

    def get_configuration(self, path = None):
        '''

        '''
        if path is None:
            path = self.config_path
            if path is None:
                device_dir = paths.device_dir

                if self.configuration_dir_name:
                    base = os.path.join(device_dir, self.configuration_dir_name)
                else:
                    base = device_dir

                self.configuration_dir_path = base
                path = os.path.join(base, '%s.cfg' % self.name)

        if  path is not None and os.path.isfile(path):
            config = self.configparser_factory()
            config.read(path)
            self.config_path = path
            return config
        else:
            self.warning('%s not a valid initialization file' % path)

    def get_configuration_writer(self):
        config = ConfigParser.RawConfigParser()
        return config

    def convert_config_name(self, name):
        '''
            @type name: C{str}
            @param name:
        '''
        nname = ''
        if '_' in name:
            for s in name.split('_'):
                if s == 'co2':
                    s = 'CO2'
                else:
                    s = s.capitalize()
                nname += s
        else:
            nname = name
        return nname
#============= EOF ====================================
