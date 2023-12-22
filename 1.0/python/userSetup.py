#!/usr/bin/env maya_to_nemo_menu
# -*- coding: utf-8 -*-
# @Time    : 2023/12/20 11:31
# @Author  : YangTao
# @File    : userSetup.py.py

import sys

from maya_tools import startup

import platform
import importlib
if platform.python_version().split(".")[0] == "3":
    reload = importlib.reload


startup.initialize()