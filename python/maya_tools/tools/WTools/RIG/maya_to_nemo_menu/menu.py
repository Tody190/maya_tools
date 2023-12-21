#!/usr/bin/env maya_to_nemo_menu
# -*- coding: utf-8 -*-
# @Time    : 2023/12/20 13:43
# @Author  : YangTao
# @File    : nemo_tools

menu_type = "menuItem"  # menu or submenu or menuItem

label = u"Maya rig 转为 Nemo rig"


def commands():
    import sys
    import os
    p = os.path.dirname(__file__)
    p in sys.path or sys.path.append(p)

    import maya_to_nemo.maya_rig_to_nemo_rig as mtn
    mtn.ex()
