# -*- coding: utf-8 -*-
"""

Script Name: 
Author: Do Trinh/Jimmy - 3D artist.

Description:


"""
# -------------------------------------------------------------------------------------------------------------
from PLM import __copyright__

from PyQt5.QtGui import QPalette

class Palette(QPalette):

    Type                            = 'DAMGPALETTE'
    key                             = 'Pallette'
    _name                           = 'DAMG Palette'
    _copyright                      = __copyright__()

    def __init__(self, *__args):
        super(Palette, self).__init__(*__args)


    @property
    def copyright(self):
        return self._copyright

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, newName):
        self._name = newName

# -------------------------------------------------------------------------------------------------------------
# Created by Trinh Do on 5/6/2020 - 3:13 AM
# © 2017 - 2020 DAMGteam. All rights reserved