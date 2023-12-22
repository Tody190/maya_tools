#!/usr/bin/env maya_to_nemo_menu
# -*- coding: utf-8 -*-
# @Time    : 2023/12/20 13:44
# @Author  : YangTao
# @File    : __init__.py


menu_type = "menuItem"  # menu or submenu or menuItem

label = u"Maya rig 转为 Nemo rig"

command = "{this_module}.maya_rig_to_nemo_rig.ex()"  # parent_module or this_module