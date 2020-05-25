# -*- coding: utf-8 -*-
"""

Script Name: Cursor.py
Author: Do Trinh/Jimmy - 3D artist.

Description:

"""
# -------------------------------------------------------------------------------------------------------------
""" Import """

from .io_gui                            import QCursor

class Cursor(QCursor):

    Type                                = 'DAMGCURSOR'
    key                                 = 'Cursor'
    _name                               = 'DAMG Cursor'

    def __init__(self, parent=None):
        QCursor.__init__(self)
        self.parent                     = parent


    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, newName):
        self._name                      = newName

# -------------------------------------------------------------------------------------------------------------
# Created by panda on 3/12/2019 - 1:36 AM
# © 2017 - 2018 DAMGteam. All rights reserved