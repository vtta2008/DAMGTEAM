# -*- coding: utf-8 -*-
"""

Script Name: UndoCommand.py
Author: Do Trinh/Jimmy - 3D artist.

Description:

"""
# -------------------------------------------------------------------------------------------------------------
""" Import """

# PyQt5
from PLM                                    import __copyright__
from PLM.api                                import QUndoCommand


class UndoCommand(QUndoCommand):

    Type                    = 'DAMGCOMMAND'
    key                     = 'UndoCommand'
    _name                   = 'DAMG Undo Command'
    _copyright              = __copyright__()

    def __init__(self):
        QUndoCommand.__init__(self)

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
# Created by panda on 6/12/2019 - 2:38 PM
# © 2017 - 2018 DAMGteam. All rights reserved