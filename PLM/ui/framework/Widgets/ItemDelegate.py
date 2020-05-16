# -*- coding: utf-8 -*-
"""

Script Name: IntemDelegate.py
Author: Do Trinh/Jimmy - 3D artist.

Description:

"""
# -------------------------------------------------------------------------------------------------------------
""" Import """

# PyQt5
from PLM                                    import __copyright__
from PLM.api                                import QItemDelegate
from PLM.plugins                            import SignalManager
from PLM.commons                            import SettingManager

class ItemDelegate(QItemDelegate):

    key                                     = 'ItemDelegate'
    Type                                    = 'DAMGITEMDELEGATE'
    _name                                   = 'DAMG Item Delegate'
    _copyright                              = __copyright__()

    def __init__(self, parent=None):
        QItemDelegate.__init__(self)

        self.parent                         = parent
        self.settings                       = self.settings = SettingManager(self)
        self.signals                        = SignalManager(self)

    @property
    def copyright(self):
        return self._copyright

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, newName):
        self._name                          = newName

# -------------------------------------------------------------------------------------------------------------
# Created by panda on 29/11/2019 - 1:03 AM
# © 2017 - 2018 DAMGteam. All rights reserved