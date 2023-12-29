#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/21 16:13
# @Author  : YangTao
# @File    : menu.py


import importlib
import inspect
import os
import platform

if platform.python_version().split(".")[0] == "3":
    reload = importlib.reload

import maya.cmds as cmds

menu_path_root = os.path.dirname(__file__).replace("\\", "/") + "/tools"

_loaded_modules = {}


def execute(cmd_str):
    import sys
    import os
    import importlib

    # get menu_setting.py path
    caller_frame = inspect.stack()[1][0]
    caller_module = inspect.getmodule(caller_frame)
    p = os.path.dirname(caller_module.__file__)
    p = p.replace('\\', '/')

    # add menu_setting.py path
    p in sys.path or sys.path.append(p)
    if p in sys.path:
        sys.path.remove(p)

    sys.path.insert(0, p)

    if cmd_str.endswith('()'):  # moudle.ex()
        modules = cmd_str.rsplit('.', 1)[0]
        fun_name = cmd_str.rsplit('.', 1)[-1].replace('()', '')
    else:
        modules = cmd_str
        fun_name = ""

    if modules not in _loaded_modules:
        _loaded_modules[modules] = importlib.import_module(modules)

    m = _loaded_modules[modules]

    # execute fun
    if fun_name:
        func = getattr(m, fun_name)
        func()


class MenuObject(object):
    def __init__(self, menu_path, menu_parent):
        # default setting
        self.menu_parent = menu_parent
        self.menu_path = menu_path.replace("\\", "/")
        self._root_path = "maya_tools/tools/"
        _this_module_str = self.menu_path.rsplit(self._root_path, 1)[-1]
        self.this_module_str = (self._root_path + _this_module_str).replace("/", ".")

        # reload module
        menu_module = importlib.import_module(self.this_module_str)
        reload(menu_module)

        # load menu_setting.py
        self.menu_setting_module = None
        self.load_menu_module()
        if self.menu_setting_module:
            # set menu_setting attr
            setattr(self.menu_setting_module, 'execute', execute)

        self.pure_obj_name = os.path.basename(menu_path).replace("_", "")
        self.object_name = "{}_{}".format(menu_parent, self.pure_obj_name)

        self.label = self.__get_menu_setting_attr("label") or os.path.basename(menu_path)

        self.menu_type = self.__get_menu_setting_attr("menu_type")

        if self.menu_type == "menu":
            self.menu_parent = "MayaWindow"

        if not self.menu_type:
            if self.menu_parent == "MayaWindow":
                self.menu_type = "menu"
            else:
                self.menu_type = "subMenu"

        self.tearOff = self.__get_menu_setting_attr("tearOff") or True

        self.command = self.__get_menu_setting_attr("command")

        self.option_command = self.__get_menu_setting_attr("option_command")


    def __get_menu_setting_attr(self, attr_name):
        if not self.menu_setting_module:
            return None
        else:
            if hasattr(self.menu_setting_module, attr_name):
                return getattr(self.menu_setting_module, attr_name)
            else:
                return None

    # def __analysis_command(self, cmd):
    #     if cmd.startswith("{this_module}"):
    #         cmd = cmd.format(this_module=self.this_module_str)
    #
    #     parent_module = cmd.rsplit(".", 1)[0]
    #
    #     return "import {0};reload({0});{1}".format(parent_module, cmd)

    def load_menu_module(self):
        # import menu.py in the dir
        for f in os.listdir(self.menu_path):
            if f == "menu_setting.py":
                # ../maya_tools/tools/WTools/ANI --> maya_tools.tools.WTools.ANI.menu
                self.menu_setting_module = importlib.import_module(self.this_module_str + ".menu_setting")
                reload(self.menu_setting_module)

    def create_menu(self):
        # rebuild the main menu
        if cmds.menu(self.object_name, exists=True):
            cmds.deleteUI(self.object_name, menu=True)

        kwargs = {'label': self.label, 'parent': self.menu_parent,
                  'tearOff': self.tearOff, 'command': self.command}

        # remove None item
        rem_k = []
        for k, v in kwargs.items():
            if v is None:
                rem_k.append(k)
        for k in rem_k:
            kwargs.pop(k)

        if self.menu_type.lower() == "menu":
            cmds.menu(self.object_name, **kwargs)

        else:
            if self.menu_type.lower() == "submenu":
                kwargs['subMenu'] = True

            if self.command:
                cmd = 'import {0};reload({0});{0}.menu_setting.'.format(self.this_module_str)
                kwargs['command'] = cmd + 'command()'

            cmds.menuItem(self.object_name, **kwargs)

            if self.option_command:
                cmd = 'import {0};reload({0});{0}.menu_setting.'.format(self.this_module_str)
                cmd += 'option_command()'

                obj_name = self.object_name + "_opt"
                cmds.menuItem(obj_name,
                              parent=self.menu_parent,
                              optionBox=True,
                              command=cmd)


def reload_menu():
    for m in _loaded_modules.values():
        try:
            reload(m)
        except Exception as e:
            print(e)

    build_menu()

    print("Menu has been reload !!!")


def build_menu(menu_path=menu_path_root,
               menu_parent="MayaWindow"):
    """
    build maya menu
    :return:
    """

    menu_obj = None
    for f in os.listdir(menu_path):
        if f.startswith("__"):  # ignore __init__, __pycache__
            continue

        f_path = os.path.join(menu_path, f).replace("\\", "/")
        if os.path.isdir(f_path):
            # menu_path = .../maya_tools/tools/WTools
            menu_obj = MenuObject(f_path, menu_parent)
            menu_obj.create_menu()

            if menu_obj.menu_type != "menuItem":
                build_menu(menu_path=f_path,
                           menu_parent=menu_obj.object_name)
    if menu_obj:
        # build reload btn
        if menu_parent == 'MayaWindow':
            cmds.menuItem(menu_obj.object_name + '_reload',
                          label=u'刷新',
                          parent=menu_obj.object_name,
                          command="from maya_tools import menu;menu.reload_menu()")