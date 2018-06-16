#!/usr/bin/env python
import os
from copy import deepcopy
from collections import OrderedDict as dict
import simplejson as json
import re

import appData as app
logger = app.logger


regex = dict(
     section        = re.compile(r"^\[[^\]\r\n]+]"),
     section_value  = re.compile(r"\[(?P<attr>[\w]*?) (?P<value>[\w\s]*?)\]$"),
     properties     = re.compile("(?P<name>[\.\w]*)\s*(?P<type>\w*)\s*(?P<value>.*)$"),
     )


PROPERTIES = dict(
    min         = 'minimum value',
    max         = 'maximum value',
    default     = 'default value',
    label       = 'node label',
    private     = 'attribute is private (hidden)',
    desc        = 'attribute description,'
)


class MetadataParser(object):

    def __init__(self, filename=None, **kwargs):

        self._template      = filename
        self._data          = dict()
        self._initialized   = False

        if filename:
            self._data = self.parse(filename)
            self._initialized = True

    def initialize(self):

        self._template = None
        self._data = dict()

    @property
    def data(self):

        import simplejson as json
        return json.dumps(self._data, indent=4)

    def parse(self, filename):

        if self._initialized:
            self.initialize()

        logger.debug('reading metadata file: "%s"' % filename)
        data = dict()
        if filename is not None:
            if os.path.exists(filename):

                parent = data
                attr_name = None  

                for line in open(filename,'r'):
                    
                    #remove newlines
                    line = line.rstrip('\n')
                    rline = line.lstrip(' ')
                    rline = rline.rstrip()

                    if not rline.startswith("#") and not rline.startswith(';') and rline.strip() != "":
                        if re.match(regex.get("section"), rline):
                            section_obj = re.search(regex.get("section_value"), rline)

                            if section_obj:
                                section_type = section_obj.group('attr')
                                section_value = section_obj.group('value')

                                # parse groups
                                if section_type == 'group':
                                    if section_value not in parent:
                                        parent = data
                                        group_data = dict()
                                        # set the current parent
                                        parent[section_value] = group_data
                                        parent = parent[section_value]
                                        #print '\nGroup: "%s"' % section_value

                                if section_type == 'attr':            
                                    attr_data = dict()
                                    # connection attributes
                                    #attr_data.update(connectable=False)
                                    #attr_data.update(connection_type=None)
                                    parent[section_value] = attr_data
                                    attr_name = section_value
                                    #print '   Attribute: "%s"' % attr_name

                                if section_type in ['input', 'output']:            
                                    conn_data = dict()
                                    conn_data.update(connectable=True)
                                    conn_data.update(connection_type=section_type)
                                    parent[section_value] = conn_data
                                    attr_name = section_value
                                    #print '   Connection: "%s"' % attr_name

                        else:
                            prop_obj = re.search(regex.get("properties"), rline)

                            if prop_obj:

                                pname = prop_obj.group('name')
                                ptype = prop_obj.group('type')
                                pvalu = prop_obj.group('value')

                                #print 'property: "%s" (%s)' % (pname, rline)
                                value = pvalu
                                if ptype in ['BOOL', 'INPUT', 'OUTPUT']:
                                    if ptype == 'BOOL':
                                        value = True if pvalu == 'true' else False

                                    # return connection types
                                    if ptype in ['INPUT', 'OUTPUT']:

                                        # data type: pvalu = FILE, DIRECTORY, ETC.
                                        value = pvalu.lower()

                                # try and get the actual value
                                else:
                                    try:
                                        value = eval(pvalu)
                                    except:
                                        logger.warning('cannot parse default value of "%s.%s": "%s" (%s)' % (attr_name, pname, pvalu, filename))
                                #print '     property: %s (%s)' % (prop_obj.group('name'), attr_name)
                                properties = {pname: {'type':ptype, 'value':value}}
                                parent[attr_name].update(properties)
                    else:
                        if rline:
                            logger.debug('skipping: "%s"' % rline)
        return data



