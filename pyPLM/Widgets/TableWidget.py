# -*- coding: utf-8 -*-
"""

Script Name: 
Author: Do Trinh/Jimmy - 3D artist.

Description:


"""
# -------------------------------------------------------------------------------------------------------------

from PySide2.QtWidgets                      import QTableWidget


class TableWidget(QTableWidget):

    Type                                    = 'DAMGUI'
    key                                     = 'TabWidget'
    _name                                   = 'DAMG Tab Widget'

    def __init__(self, *__args):
        super(TableWidget, self).__init__(*__args)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        self._name                          = val

# -------------------------------------------------------------------------------------------------------------
# Created by Trinh Do on 5/6/2020 - 3:13 AM
# © 2017 - 2020 DAMGteam. All rights reserved