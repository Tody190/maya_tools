#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/28 14:04
# @Author  : YangTao

menu_type = "menuItem"  # menu or submenu or menuItem

label = u"切换为 Nemo Rig"


def command():
    execute('maya_tools.tools.nemo_switcher.switch()')


def option_command():
    import os
    help_url = 'https://cg.wlf.com/zh/%E7%8E%AF%E8%8A%82/%E7%BB%91%E5%AE%9A%E5%B7%A5%E5%85%B7/nemo_switchernemo_switcher'
    os.startfile(help_url)