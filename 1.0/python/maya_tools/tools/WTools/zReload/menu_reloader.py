#!/usr/bin/env python
# -*- coding: utf-8 -*-

import platform
import importlib
if platform.python_version().split(".")[0] == "3":
    reload = importlib.reload


def reload_menu():
    from maya_tools import menu
    reload(menu)
    menu.build_menu()
    print("Menu has been reload !!!")