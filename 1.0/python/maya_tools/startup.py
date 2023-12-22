#!/usr/bin/env maya_to_nemo_menu
# -*- coding: utf-8 -*-
# @Time    : 2023/12/20 11:30
# @Author  : YangTao
# @File    : startup.py

import platform
import importlib

if platform.python_version().split(".")[0] == "3":
    reload = importlib.reload

import maya.utils as utils


def build_menu():
    import maya_tools.menu as menu
    reload(menu)
    menu.build_menu()


def initialize():
    # build maya menu
    utils.executeDeferred(build_menu)
