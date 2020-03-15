# -*- coding: utf-8 -*-
"""

Script Name: UiSignals.py
Author: Do Trinh/Jimmy - 3D artist.

Description:

"""
# -------------------------------------------------------------------------------------------------------------
""" Import """

# PLM
from .base                              import SignalBase

# -------------------------------------------------------------------------------------------------------------
""" Signal class: setup all the signal which will be using. """

class SignalManager(SignalBase):

    key                             = "SignalManager"

    def __init__(self, parent=None):
        super(SignalManager, self).__init__(parent)

        self.parent                 = parent

        if self.parent:
            self.changeParent(self.parent)



# -------------------------------------------------------------------------------------------------------------
# Created by panda on 25/10/2019 - 6:59 AM
# © 2017 - 2018 DAMGteam. All rights reserved