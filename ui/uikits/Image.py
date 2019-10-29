# -*- coding: utf-8 -*-
"""

Script Name: Image.py
Author: Do Trinh/Jimmy - 3D artist.

Description:

"""
# -------------------------------------------------------------------------------------------------------------
from __future__ import absolute_import, unicode_literals

import os

from PyQt5.QtGui                import QImage

from appData                    import SETTING_FILEPTH, ST_FORMAT, __copyright__
from cores.SignalManager        import SignalManager
from cores.Loggers              import Loggers
from cores.Settings             import Settings
from utils                      import get_avatar_image


class Image(QImage):

    Type                        = 'DAMGUI'
    key                         = 'Image'
    _name                       = 'DAMG Image'
    _copyright                  = __copyright__
    _data                       = dict()

    def __init__(self, image=None, parent=None):

        self.image              = image
        self.parent             = parent
        self.signals            = SignalManager(self)
        self.logger             = Loggers(self.__class__.__name__)
        self.settings           = Settings(SETTING_FILEPTH['app'], ST_FORMAT['ini'], self)

        if self.image is None:
            print("IMAGEISNONEERROR: Image should be a name or a path, not None")
        else:
            if not os.path.exists(self.image):
                if os.path.exists(get_avatar_image(self.image)):
                    self.avata(self.image)
                else:
                    print("IMAGENOTFOUND: Could not find image: {0}".format(self.image))
            else:
                Image(self.image)

    def avata(self, image):
        return Image(get_avatar_image(image))

    def setValue(self, key, value):
        return self.settings.initSetValue(key, value, self.key)

    def getValue(self, key):
        return self.settings.initValue(key, self.key)

    @property
    def copyright(self):
        return self._copyright

    @property
    def data(self):
        return self._data

    @property
    def name(self):
        return self._name

    @data.setter
    def data(self, newData):
        self._data              = newData

    @name.setter
    def name(self, newName):
        self._name              = newName


# -------------------------------------------------------------------------------------------------------------
# Created by panda on 30/10/2019 - 1:33 AM
# © 2017 - 2018 DAMGteam. All rights reserved