# -*- coding: utf-8 -*-
"""

Script Name: Painter.py
Author: Do Trinh/Jimmy - 3D artist.

Description:
    

"""
# -------------------------------------------------------------------------------------------------------------
""" Import """


from PySide2.QtGui                          import QPainter


class Painter(QPainter):

    Type                        = 'DAMGPAINTER'
    key                         = 'Painter'
    _name                       = 'DAMG Painter'

    def __init__(self):
        super(Painter, self).__init__()


    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, newName):
        self._name              = newName

# -------------------------------------------------------------------------------------------------------------
# Created by panda on 3/20/2020 - 5:31 AM
# © 2017 - 2019 DAMGteam. All rights reserved