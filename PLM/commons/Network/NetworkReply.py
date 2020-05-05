# -*- coding: utf-8 -*-
"""

Script Name: 
Author: Do Trinh/Jimmy - 3D artist.

Description:


"""
# -------------------------------------------------------------------------------------------------------------
from PLM import __copyright__

from PyQt5.QtNetwork                    import QNetworkReply

class NetworkReply(QNetworkReply):

    Type                                = 'DAMGNETWORKREPLY'
    key                                 = 'NetworkReply'
    _name                               = 'DAMG Network Reply'
    _copyright                          = __copyright__()

    def __init__(self, parent):
        super(NetworkReply, self).__init__(parent)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        self._name = val

    @property
    def copyright(self):
        return self._copyright

# -------------------------------------------------------------------------------------------------------------
# Created by Trinh Do on 5/6/2020 - 3:13 AM
# © 2017 - 2020 DAMGteam. All rights reserved