# -*- coding: utf-8 -*-
"""

Script Name: HiddenLayout.py
Author: Do Trinh/Jimmy - 3D artist.

Description:

"""
# -------------------------------------------------------------------------------------------------------------

from pyPLM.Widgets import LineEdit, ShortCut
from PLM.options import FRAMELESS, KEY_RETURN
from pyPLM.loggers import DamgLogger
from PLM import APP_LOG

class CommandUI(LineEdit):

    key                         = 'CommandUI'

    def __init__(self, parent=None):
        super(CommandUI, self).__init__({}, parent)

        self.parent             = parent
        self.resize(250, 25)
        self.logger             = DamgLogger(self, filepth=APP_LOG)

        self.setWindowFlags(FRAMELESS)
        self.addAction(ShortCut(shortcut='Esc', trigger=self.hide, parent=self))

    def keyReleaseEvent(self, event):
        if event.key() == KEY_RETURN:
            self.run()

    def run(self):
        key                     = self.text()
        self.setText('')
        self.parent.command(key)
        self.close()




# -------------------------------------------------------------------------------------------------------------
# Created by panda on 11/11/2019 - 5:30 PM
# © 2017 - 2018 DAMGteam. All rights reserved