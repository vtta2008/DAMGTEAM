# -*- coding: utf-8 -*-
"""

Script Name: TabBar.py
Author: Do Trinh/Jimmy - 3D artist.

Description:

"""
# -------------------------------------------------------------------------------------------------------------
""" Import """

# PyQt5
from PLM                                    import __copyright__
from PLM.api                                import QTabWidget
from PLM.plugins.SignalManager              import SignalManager
from PLM.data.SettingManager import SettingManager


class TabWidget(QTabWidget):

    Type                                    = 'DAMGUI'
    key                                     = 'TabWidget'
    _name                                   = 'DAMG Tab Widget'
    _copyright                              = __copyright__()

    def __init__(self, parent=None):
        QTabWidget.__init__(self)

        self.parent                         = parent
        self.settings = SettingManager(self)
        self.signals = SignalManager(self)

        self.setTabPosition(self.North)
        self.setMovable(True)

        self.values = dict(w = self.width(), h = self.height(), x = self.x(), y = self.y())

    def setValue(self, key, value):
        return self.settings.initSetValue(key, value, self.key)

    def getValue(self, key, decode=None):
        if decode is None:
            return self.settings.initValue(key, self.key)
        else:
            return self.settings.initValue(key, self.key, decode)

    @property
    def copyright(self):
        return self._copyright

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, newName):
        self._name                      = newName

    def getCurrentTab(self):
        return self.tabLst[self.currentIndex()]

    def getCurrentKey(self):
        return self.getCurrentTab().key


# -------------------------------------------------------------------------------------------------------------
# Created by panda on 27/10/2019 - 4:39 PM
# © 2017 - 2018 DAMGteam. All rights reserved