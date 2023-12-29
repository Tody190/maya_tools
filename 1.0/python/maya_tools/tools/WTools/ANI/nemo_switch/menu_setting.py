#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/28 14:04
# @Author  : YangTao

menu_type = "menuItem"  # menu or submenu or menuItem


label = u"切换为 Nemo Rig"


def command():
    execute('switch_to_nemo.switch()')