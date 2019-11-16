# -*- coding: utf-8 -*-
"""

Script Name: TextSteam.py
Author: Do Trinh/Jimmy - 3D artist.

Description:

"""
# -------------------------------------------------------------------------------------------------------------
from __future__ import absolute_import, unicode_literals


from PyQt5.QtCore                           import QTextStream

from appData                                import __copyright__


class TextStream(QTextStream):

    Type                                    = 'DAMGSTREAM'
    key                                     = 'TextStream'
    _name                                   = 'DAMG Text Stream'
    _copyright                              = __copyright__

    @property
    def copyright(self):
        return self._copyright

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, newName):
        self._name                      = newName

# -------------------------------------------------------------------------------------------------------------
# Created by panda on 15/11/2019 - 5:43 PM
# © 2017 - 2018 DAMGteam. All rights reserved