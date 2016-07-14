#!/usr/bin/env python
#
#   Copyright (c) 2016 In-Q-Tel, Inc, All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
"""
Rest module for PoseidonConfig. Delivers
settings from the poseidon configuration
file.

Created on 17 May 2016
@author: dgrossman, lanhamt
"""
import ConfigParser
import json
import os

from poseidon.baseClasses.Monitor_Action_Base import Monitor_Action_Base
from poseidon.baseClasses.Monitor_Helper_Base import Monitor_Helper_Base


# poseidonWork created in docker containers
config_template_path = '/poseidonWork/templates/config.template'


class Config(Monitor_Action_Base):
    """Poseidon Action Rest Interface"""

    def __init__(self):
        super(Config, self).__init__()
        self.mod_name = self.__class__.__name__
        self.config = ConfigParser.ConfigParser()
        if os.environ.get('POSEIDON_CONFIG') is not None:
            print 'From the Environment'
            self.config_path = os.environ.get('POSEIDON_CONFIG')
        else:
            print 'From the hardcoded value'
            self.config_path = config_template_path
        self.config.readfp(open(self.config_path))

    def add_endpoint(self, name, handler):
        a = handler()
        a.owner = self
        self.actions[name] = a

    def del_endpoint(self, name):
        if name in self.actions:
            self.actions.pop(name)

    def get_endpoint(self, name):
        if name in self.actions:
            return self.actions.get(name)
        else:
            return None


class Handle_FullConfig(Monitor_Helper_Base):
    """
    Provides the full configuration file in json dict string
    with sections as keys and their key-value pairs as values.
    """

    def __init__(self):
        self.mod_name = self.__class__.__name__
        self.owner = None

    def direct_get(self):
        retval = None
        try:
            ret = {}
            for sec in self.owner.config.sections():
                ret[sec] = self.owner.config.items(sec)
            retval = json.dumps(ret)
        except:
            retval = json.dumps('Failed to open config file.')
        return retval

    def on_get(self, req, resp):
        resp.body = self.direct_get()


class Handle_SectionConfig(Monitor_Helper_Base):
    """
    Given a section name in the config file,
    returns a json list string of all the key-value
    pairs under that section.
    """

    def __init__(self):
        self.mod_name = self.__class__.__name__
        self.owner = None

    # direct way
    def direct_get(self, section):
        # print '*************** %s getting %s' % (self.mod_name,section)
        retval = None
        try:
            retval = self.owner.config.items(section)
        except:
            retval = 'Failed to find section: %s' % (section)
        return retval

    # rest way
    def on_get(self, req, resp, section):
        ret_sec = self.direct_get(section)
        resp.body = json.dumps(ret_sec)


class Handle_FieldConfig(Monitor_Helper_Base):
    """
    Given a section and corresponding key in the config
    file, returns the value as a string.
    """

    def __init__(self):
        self.mod_name = self.__class__.__name__
        self.owner = None

    def direct_get(self, field, section):
        retval = ''
        try:
            retval = self.owner.config.get(section, field)
        except:
            retval = 'Can\'t find field: %s in section: %s' % (field, section)
        return retval

    def on_get(self, req, resp, section, field):
        """
        Requests should have a section of the config
        file and variable/field in that section to be
        returned in the response body.
        """
        resp.content_type = 'text/text'
        resp.body = self.direct_get(field, section)


config_interface = Config()
config_interface.add_endpoint('Handle_FieldConfig', Handle_FieldConfig)
config_interface.add_endpoint('Handle_SectionConfig', Handle_SectionConfig)
config_interface.add_endpoint('Handle_FullConfig', Handle_FullConfig)
