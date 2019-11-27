# -*- coding: utf-8 -*-
"""

Script Name: TextSteam.py
Author: Do Trinh/Jimmy - 3D artist.

Description:

"""
# -------------------------------------------------------------------------------------------------------------
from __future__ import absolute_import, unicode_literals
from __buildtins__ import __copyright__, settings, signals


from PyQt5.QtCore                           import QTextStream


class TextStream(QTextStream):

    Type                                    = 'DAMGSTREAM'
    key                                     = 'TextStream'
    _name                                   = 'DAMG Text Stream'
    _copyright                              = __copyright__()

    def __init__(self, fileName, parent=None):
        super(TextStream, self).__init__(fileName)

        self.parent                         = parent
        self.settings                       = settings
        self.signals                        = signals
        self.settings.changeParent(self)
        self.signals.changeParent(self)

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