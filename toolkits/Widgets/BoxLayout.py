# -*- coding: utf-8 -*-
"""

Script Name: VBoxLayout.py
Author: Do Trinh/Jimmy - 3D artist.

Description:

"""
# -------------------------------------------------------------------------------------------------------------
from __future__ import absolute_import, unicode_literals
from __buildtins__ import __copyright__
""" Import """

# PyQt5
from PyQt5.QtWidgets                        import QVBoxLayout, QHBoxLayout

# PLM
from utils                                  import check_preset
from appData                                import SETTING_FILEPTH, ST_FORMAT
from cores.Settings                         import Settings
from cores.SignalManager                    import SignalManager

class HBoxLayout(QHBoxLayout):

    Type                                    = 'DAMGUI'
    key                                     = 'HBoxLayout'
    _name                                   = 'DAMG H Box Layout'
    _copyright                              = __copyright__()

    def __init__(self, preset={}, parent=None):
        QHBoxLayout.__init__(self)
        self.parent                         = parent
        self.settings = Settings(SETTING_FILEPTH['app'], ST_FORMAT['ini'], self)
        self.signals = SignalManager(self)

        self.preset = preset
        if check_preset(self.preset):
            self.buildUI()

    def buildUI(self):
        for key, value in self.preset.items():
            if key == 'addWidget':
                for widget in value:
                    self.addWidget(widget)
            elif key == 'addLayout':
                for layout in value:
                    self.addLayout(layout)
            elif key == 'addStretch':
                self.setStretch(value, 0)
            else:
                print("{0}: Unrecognise configKey: {1}".format(__name__, key))

    @property
    def copyright(self):
        return self._copyright

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, newName):
        self._name                      = newName


class VBoxLayout(QVBoxLayout):

    Type                                    = 'DAMGUI'
    key                                     = 'VBoxLayout'
    _name                                   = 'DAMG V Box Layout'
    _copyright                              = __copyright__()

    def __init__(self, preset={}, parent=None):
        QVBoxLayout.__init__(self)
        self.parent                         = parent
        self.settings = Settings(SETTING_FILEPTH['app'], ST_FORMAT['ini'], self)
        self.signals = SignalManager(self)

        self.preset                         = preset
        if check_preset(self.preset):
            self.buildUI()

    def buildUI(self):
        for key, value in self.preset.items():
            if key == 'addWidget':
                for widget in value:
                    self.addWidget(widget)
            elif key == 'addLayout':
                for layout in value:
                    self.addLayout(layout)
            elif key == 'addStretch':
                self.setStretch(value, 0)
            else:
                print("Unrecognise configKey: {}".format(key))

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
# Created by panda on 27/10/2019 - 6:57 PM
# © 2017 - 2018 DAMGteam. All rights reserved