# -*- coding: utf-8 -*-
"""

Script Name: __init__.py.py
Author: Do Trinh/Jimmy - 3D artist.

Description:
    

"""
# -------------------------------------------------------------------------------------------------------------
import os, sys
import winshell

shortcuts = {}

user_programs = winshell.programs()
for dirpath, dirnames, filenames in os.walk(user_programs):
    relpath = dirpath[1 + len(user_programs):]
    shortcuts.setdefault(
        relpath, []
    ).extend(
        [winshell.shortcut(os.path.join(dirpath, f)) for f in filenames]
    )

all_programs = winshell.programs(common=1)
for dirpath, dirnames, filenames in os.walk(all_programs):
    relpath = dirpath[1 + len(all_programs):]
    shortcuts.setdefault(relpath, []).extend([winshell.shortcut(os.path.join(dirpath, f)) for f in filenames])

for relpath, lnks in sorted(shortcuts.items()):
    level = relpath.count("\\")
    if level == 0:
        print("")
    print("%s+ %s" % ("    " * level, relpath))
    for lnk in lnks:
        name, _ = os.path.splitext(os.path.basename(lnk.lnk_filepath))
        print("%s* %s -> %s" % ("    " * (level + 1), name, lnk.path))

# -------------------------------------------------------------------------------------------------------------
# Created by panda on 3/16/2020 - 2:17 AM
# © 2017 - 2019 DAMGteam. All rights reserved