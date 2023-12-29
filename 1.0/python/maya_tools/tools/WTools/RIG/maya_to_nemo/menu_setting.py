#!/usr/bin/env maya_to_nemo_menu
# -*- coding: utf-8 -*-
# @Time    : 2023/12/20 13:43
# @Author  : YangTao
# @File    : nemo_tools
import os

menu_type = "menuItem"  # menu or submenu or menuItem

label = u"Maya rig 转为 Nemo rig"

# command = 'import {this_module}.maya_to_nemo.maya_rig_to_nemo_rig;'
# command += 'reload({this_module}.maya_to_nemo.maya_rig_to_nemo_rig)'
# command += '{this_module}.maya_to_nemo.maya_rig_to_nemo_rig.go()'

def command():
    execute('maya_rig_to_nemo_rig.go()')

def option_command():
    import os
    help_url = 'https://cg.wlf.com/zh/%E7%8E%AF%E8%8A%82/%E7%BB%91%E5%AE%9A%E5%B7%A5%E5%85%B7/maya_rig_to_nemo_rig'
    os.startfile(help_url)