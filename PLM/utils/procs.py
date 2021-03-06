# -*- coding: utf-8 -*-
"""

Script Name: 
Author: Do Trinh/Jimmy - 3D artist.

Description:


"""
# -------------------------------------------------------------------------------------------------------------

import platform, subprocess, os, sys

from psutil                 import cpu_percent, virtual_memory, disk_usage
from GPUtil                 import getGPUs
from .converts              import byte2gb, mb2gb
from pyPLM.Core             import DateTime, Date, Time

def create_datetime(hour=0, minute=0, second=0, day=1, month=1, year=None):

    if not year:
        year = int(Date().currentDate().year())
    elif year < 99:
        year = int("20{0}".format(year))
    else:
        year = int(year)

    if month > 12:
        raise IndexError('Expect month smaller than 12: {0}'.format(month))

    if month in [1, 3, 5, 7, 8, 10, 12]:
        days = 31
    elif month in [2]:
        days = 28
    else:
        days = 30

    if day > days:
        raise IndexError('Expect day smaller than (0): {1}'.format(days, day))

    if hour > 24:
        raise IndexError('Expect hour smaller than 24: {0}'.format(hour))

    if minute > 60:
        raise IndexError('Expect minute smaller than 60: {0}'.format(minute))

    if second > 60:
        raise IndexError('Expect second smaller than 60: {0}'.format(second))

    date = Date(year, month, day)
    time = Time(hour, minute, second)

    return DateTime(date, time)


def obj_properties_setting(directory, mode):
    if platform.system() == "Windows" or platform.system() == "Darwin":
        if mode == "h":
            if platform.system() == "Windows":
                subprocess.call(["attrib", "+H", directory])
            elif platform.system() == "Darwin":
                subprocess.call(["chflags", "hidden", directory])
        elif mode == "s":
            if platform.system() == "Windows":
                subprocess.call(["attrib", "-H", directory])
            elif platform.system() == "Darwin":
                subprocess.call(["chflags", "nohidden", directory])
        else:
            print("ERROR: (Incorrect Command) Valid commands are 'HIDE' and 'UNHIDE' (both are not case sensitive)")
    else:
        print("ERROR: (Unknown Operating System) Only Windows and Darwin(Mac) are Supported")

def change_permissions_recursive(path, mode):
    for root, dirs, files in os.walk(path, topdown=False):
        for dir in [os.path.join(root,d) for d in dirs]:
            os.chmod(dir, mode)
    for file in [os.path.join(root, f) for f in files]:
            os.chmod(file, mode)

def batch_obj_properties_setting(listObj, mode):

    for obj in listObj:
        if os.path.exists(obj):
            obj_properties_setting(obj, mode)
        else:
            print('Could not find the specific path: %s' % obj)

# -------------------------------------------------------------------------------------------------------------
""" Command Prompt """

def cmd_execute_py(name, directory):
    """
    Executing a python file
    :param name: python file name
    :param directory: path to python file
    :return: executing in command prompt
    """
    print("Executing {name} from {path}".format(name=name, path=directory))
    pth = os.path.join(directory, name)
    if os.path.exists(pth):
        return subprocess.call([sys.executable, pth])
    else:
        print("Path: {} does not exist".format(directory))

def system_call(args, cwd="."):
    print("Running '{}' in '{}'".format(str(args), cwd))
    return subprocess.call(args, cwd=cwd)

def run_cmd(pth):
    return subprocess.Popen(pth)

def open_cmd():
    return os.system("start /wait cmd")


def install_pyPackage(name=None, version=None):

    if name:
        if not version:
            subprocess.Popen('python -m pip install {0} --user --upgrade'.format(name), shell=True).wait()
        else:
            subprocess.Popen('python -m pip install {0}={1} --user'.format(name, version), shell=True).wait()
    else:
        print("Cannot find package name: {0}".format(name))


def uninstall_pyPackage(name=None):

    if name:
        subprocess.Popen('python -m pip uninstall {0}'.format(name), shell=True).wait()
    else:
        print("Cannot find package name: {0}".format(name))

# -------------------------------------------------------------------------------------------------------------
""" PC performance """

def get_cpu_useage(interval=1, percpu=False):
    return cpu_percent(interval, percpu)

def get_ram_total():
    return byte2gb(virtual_memory()[0])

def get_ram_useage():
    return virtual_memory()[2]

def get_gpu_total():
    gpus = getGPUs()
    total = 0.0
    for gpu in gpus:
        total += float(gpu.memoryTotal)
    return mb2gb(total)

def get_gpu_useage():
    gpus = getGPUs()
    used = 0.0
    for gpu in gpus:
        used += float(gpu.memoryUsed/gpu.memoryTotal*100)
    rate = used/len(gpus)
    return round(rate, 2)

def get_disk_total():
    disk = disk_usage('/')
    return round(disk.total/(1024**3))

def get_disk_used():
    disk = disk_usage('/')
    return round(disk.used/(1024**3))

def get_disk_free():
    disk = disk_usage('/')
    return round(disk.free/(1024**3))

def get_disk_useage():
    disk = disk_usage('/')
    return disk.percent



# -------------------------------------------------------------------------------------------------------------
# Created by Trinh Do on 5/6/2020 - 3:13 AM
# © 2017 - 2020 DAMGteam. All rights reserved