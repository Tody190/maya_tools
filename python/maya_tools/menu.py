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


def execute(cmd_str):
    import sys
    import os
    import importlib
    import platform
    if platform.python_version().split(".")[0] == "3":
        reload = importlib.reload

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
        fun_name = cmd_str.rsplit('.', 1)[-1].replace("()", "")
    else:
        modules = cmd_str
        fun_name = ""

    # reload module
    m = importlib.import_module(modules)
    reload(m)

    # execute fun
    if fun_name:
        func = getattr(m, fun_name)
        func()


class MenuObject(object):
    def __init__(self, menu_path, menu_parent):
        # default setting
        self.menu_parent = menu_parent
        self.menu_path = menu_path.replace("\\", "/")

        self.menu_module = None
        self.load_menu_module()

        obj_name = os.path.basename(menu_path).replace("_", "")
        self.object_name = "{}_{}".format(menu_parent, obj_name)

        self.label = self.__get_attr("label") or os.path.basename(menu_path)

        self.menu_type = self.__get_attr("menu_type")

        if self.menu_type == "menu":
            self.menu_parent = "MayaWindow"

        if not self.menu_type:
            if self.menu_parent == "MayaWindow":
                self.menu_type = "menu"
            else:
                self.menu_type = "subMenu"

        self.tearOff = self.__get_attr("tearOff") or True

        if self.menu_module:
            # add fun to module
            setattr(self.menu_module, "easy_command", execute)


    def __get_attr(self, attr_name):
        if not self.menu_module:
            return None
        else:
            if hasattr(self.menu_module, attr_name):
                return getattr(self.menu_module, attr_name)
            else:
                return None


    def load_menu_module(self):
        # import menu.py in the dir
        for f in os.listdir(self.menu_path):
            if f == "menu_setting.py":
                # ../maya_tools/tools/WTools/ANI --> maya_tools.tools.WTools.ANI.menu
                module_name ="tools.{}.menu_setting".format(self.menu_path.split("/{}/".format("tools"), 1)[-1].replace("/", "."))

                self.menu_module = importlib.import_module(module_name)
                reload(self.menu_module)

    def create_menu(self):
        # rebuild the main menu
        if cmds.menu(self.object_name, exists=True):
            cmds.deleteUI(self.object_name, menu=True)

        if self.menu_type == "menu":
            cmds.menu(self.object_name,
                    label=self.label,
                    parent=self.menu_parent,
                    tearOff=self.tearOff)

        elif self.menu_type == "subMenu":
            cmds.menuItem(self.object_name,
                        subMenu=True,
                        label=self.label,
                        parent=self.menu_parent,
                        tearOff=self.tearOff)

        elif self.menu_type == "menuItem":
            # ../maya_tools/tools/WTools/ANI --> maya_tools.tools.WTools.ANI.menu
            module_name = "tools.{}.menu_setting".format(
                self.menu_path.split("/{}/".format("tools"), 1)[-1].replace("/", "."))

            cmd = "import {};reload({});{}.commands()".format(module_name,
                                                              module_name,
                                                              module_name)

            cmds.menuItem(self.object_name,
                        label=self.label,
                        parent=self.menu_parent,
                        tearOff=self.tearOff,
                        command=cmd)


def build_menu(menu_path=menu_path_root,
               menu_parent="MayaWindow"):
    """
    build maya menu
    :return:
    """
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
