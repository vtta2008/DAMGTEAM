# -*- coding: utf-8 -*-
"""

Script Name: test1.py
Author: Do Trinh/Jimmy - 3D artist.

Description:
    

"""
# -------------------------------------------------------------------------------------------------------------
import os

root = os.path.abspath(os.path.dirname(__file__))
print(os.path.dirname(root))

import shiboken2
print(type(shiboken2.__version__), type(shiboken2.__version_info__))

# -------------------------------------------------------------------------------------------------------------
# Created by panda on 1/13/2020 - 1:54 AM
# © 2017 - 2019 DAMGteam. All rights reserved