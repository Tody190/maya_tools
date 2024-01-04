#!/usr/bin/env maya_to_nemo_menu
# -*- coding: utf-8 -*-
# @Time    : 2023/12/20 11:30
# @Author  : YangTao
# @File    : startup.py
import os
import platform
import importlib

if platform.python_version().split(".")[0] == "3":
    reload = importlib.reload

import maya.utils as utils
import maya.cmds as cmds


def build_menu():
    import maya_tools.menu as menu
    reload(menu)
    menu.build_menu()


def add_callbacks():
    pass


def setting():
    """
    Some initialization settings that can only be done in Maya
    Values are usually passed through environment variables
    :return:
    """
    evaluation_manager_mode = os.environ.get('YT_MAYA_EVALUATION_MANAGER_MODE', None)
    if evaluation_manager_mode is not None:
        cmds.evaluationManager(mode=evaluation_manager_mode)
        print("----------------------")
        print("set maya evaluation manager mode to: %s" % evaluation_manager_mode)
        print("----------------------")


def initialize():
    # build maya menu
    utils.executeDeferred(build_menu)
    # add callbacks
