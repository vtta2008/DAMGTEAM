# -*- coding: utf-8 -*-
"""
Script Name: Credit.py
Author: Do Trinh/Jimmy - 3D artist.

Description:
    Credit infomation.

"""
# -------------------------------------------------------------------------------------------------------------
""" Import """

# Python
import sys
from functools                      import partial

# PtQt5
from PyQt5.QtWidgets                import QApplication, QScrollArea

# Plm
from appData                        import CODECONDUCT
from ui.uikits.Widget                         import Widget
from ui.uikits.Button import Button
from ui.uikits.Label import Label
from ui.uikits.GridLayout import GridLayout


# -------------------------------------------------------------------------------------------------------------
""" CodeConduct Layout """

class CodeConduct(Widget):

    key = 'CodeConduct'

    def __init__(self, parent=None):

        super(CodeConduct, self).__init__(parent)
        # self.setWindowIcon(AppIcon(32, 'CodeConduct'))
        self.setWindowTitle("CODE OF CONDUCT")

        self.layout                 = GridLayout()
        self.buildUI()
        self.setLayout(self.layout)
        self.resize(650, 800)

    def buildUI(self):
        self.scrollArea             = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.content                = Label({'txt':CODECONDUCT, 'alg':'left', 'link': True})

        self.content.setGeometry(0, 0, 650, 800)
        self.scrollArea.setWidget(self.content)

        closeBtn                    = Button({'txt': 'Close', 'tt': 'Close window', 'cl': partial(self.close)})

        self.layout.addWidget(self.scrollArea, 0, 0, 8, 4)
        self.layout.addWidget(closeBtn, 8, 3, 1, 1)

def main():
    app = QApplication(sys.argv)
    about_layout = CodeConduct()
    about_layout.show()
    app.exec_()

if __name__=='__main__':
    main()