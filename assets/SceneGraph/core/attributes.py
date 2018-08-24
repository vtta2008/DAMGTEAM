#!/usr/bin/env python
import json
import weakref
from collections import OrderedDict as dict
import util


class Attribute(object):
    """
    Generic Attribute class.
    """
    attribute_type = 'generic'
    REQUIRED       = ['name', 'attr_type', 'value', '_edges']

    def __init__(self, name, value, dagnode=None, user=True, **kwargs):

        # private attributes
        self._dag              = weakref.ref(dagnode) if dagnode else None

        # stash argument passed to 'type' - overrides 
        # auto-type mechanism. * this will become data_type
        self._type             = kwargs.get('attr_type', None)
        self._edges            = []

        self.name              = name
        self.label             = kwargs.get('label', "") 
        self.default_value     = kwargs.get('default_value', "")
        self.value             = value
        
        self.doctstring        = kwargs.get('doctstring', '')
        self.desc              = kwargs.get('desc', '')

        # globals
        self.user              = user
        self.private           = kwargs.get('private', False)  # hidden
        self.hidden            = kwargs.get('hidden', False) 
        self.connectable       = kwargs.get('connectable', False)
        self.locked            = kwargs.get('locked', False)
        self.required          = kwargs.get('required', False)

        # connection
        self.connection_type   = kwargs.get('connection_type', 'input')
        self.data_type         = kwargs.get('data_type', None) 
        self.max_connections   = kwargs.get('max_connections', 1)  # 0 = infinite

        if self.connectable:
            #print 'Connection "%s" attr_type:  %s' %  (self.name, self._type)
            #print 'Connection "%s" data_type:  %s' % (self.name, self.data_type)
            pass

    def __str__(self):
        return json.dumps({self.name:self.data}, indent=4)

    def __repr__(self):
        return json.dumps({self.name:self.data}, indent=4)

    def update(self, **kwargs):
        """
        Update attributes.

        .. todo::
            - can't pass as **kwargs else we lose the order (why is that?)
        """
        for name, value in kwargs.iteritems():
            if value not in [None, 'null']:
                # we don't save edge attributes, so don't read them from disk.
                if name not in ['_edges']:
                    #print '# adding attribute: "%s"' % name
                    if hasattr(self, name) and value != getattr(self, name):
                        print('# DEBUG: Attribute "%s" updating value: "%s": "%s" - "%s"' % (self.name, name, value, getattr(self, name)))
                    setattr(self, name, value)

    @property
    def data(self):
        """
        Output data for writing.

        :returns: attribute data.
        :rtype: dict
        """
        data = dict()
        #for attr in self.REQUIRED:
        for attr in ['label', 'value', 'desc', '_edges', 'attr_type', 'private', 
                     'hidden', 'connectable', 'connection_type', 'locked', 'required', 'user']:
                if hasattr(self, attr):
                    value = getattr(self, attr)
                    if value or attr in self.REQUIRED:
                        #if value or attr in self.REQUIRED:
                        data[attr] = value
        return data

    @property
    def dagnode(self):
        """
        :returns: dag node parent.
        :rtype: DagNode
        """
        return self._dag()

    @property
    def attr_type(self):
        if self._type is not None:
            return self._type
        return util.attr_type(self.value)

    @attr_type.setter
    def attr_type(self, val):
        self._type = val

    @property
    def is_input(self):
        """
        :returns: attribute is an input connection.
        :rtype: bool
        """
        if not self.connectable:
            return False
        return self.connection_type == 'input'

    @property
    def is_output(self):
        """
        :returns: attribute is an output connection.
        :rtype: bool
        """
        if not self.connectable:
            return False
        return self.connection_type == 'output'

    def rename(self, name):
        """
        Rename the attribute.

        :param str name: new name.
        """
        old_name = self.name
        self.name = name

