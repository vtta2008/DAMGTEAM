#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Script Name: setup.py
Author: Do Trinh/Jimmy - 3D artist.
Description:
    This script will build executable file.

"""
# -------------------------------------------------------------------------------------------------------------
""" Import """
import os
import sys
import setuptools
from cx_Freeze import setup, Executable

import appData as app
from utilities import utils as func

base = None

if sys.platform == "win32":
    base = "Win32GUI"

os.environ[app.__envKey__] = os.getcwd()

for dir in os.listdir(os.getenv(app.__envKey__)):
    pltPth = os.path.join(os.getenv(app.__envKey__), dir)
    if os.path.isdir(pltPth):
        if not pltPth in sys.path:
            sys.path.append(pltPth)

with open('README.rst', 'r') as f:
    readme = f.read()

includes = ["atexit", "re"]

setup(
    name = func.read_package_variable("__project__"),
    version = func.read_package_variable("__version__"),
    packages = setuptools.find_packages(),
    package_dir = func.read_package_variable("__packages_dir__"),
    url = func.read_package_variable("__website__"),
    download_url = func.read_package_variable("__download__"),
    license = func.read_package_variable("__licence__"),
    author = func.read_package_variable("__author__"),
    author_email= func.read_package_variable("__email__"),
    maintainer = func.read_package_variable("__author__"),
    maintainer_email = func.read_package_variable("__email__"),
    description = func.read_package_variable("__description__"),
    long_description = readme,
    py_modules = func.read_package_variable("__modules__"),
    install_requires =func.read_package_variable("__description__"),
    classifiers = func.read_package_variable("__classifiers__"),
    options = {"build_exe" : {"includes" : includes }},
    executables = [Executable("Plt.py", base = base)],
)
