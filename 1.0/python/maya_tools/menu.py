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


# def execute(cmd_str):
#     import sys
#     import os
#     import importlib
#     import platform
#     if platform.python_version().split(".")[0] == "3":
#         reload = importlib.reload
#
#     # get menu_setting.py path
#     caller_frame = inspect.stack()[1][0]
#     caller_module = inspect.getmodule(caller_frame)
#     p = os.path.dirname(caller_module.__file__)
#     p = p.replace('\\', '/')
#
#     # add menu_setting.py path
#     p in sys.path or sys.path.append(p)
#     if p in sys.path:
#         sys.path.remove(p)
#
#     sys.path.insert(0, p)
#
#     if cmd_str.endswith('()'):  # moudle.ex()
#         modules = cmd_str.rsplit('.', 1)[0]
#         fun_name = cmd_str.rsplit('.', 1)[-1].replace('()', '')
#     else:
#         modules = cmd_str
#         fun_name = ""
#
#     # reload module
#     m = importlib.import_module(modules)
#     reload(m)
#
#     # execute fun
#     if fun_name:
#         func = getattr(m, fun_name)
#         func()


class MenuObject(object):
    def __init__(self, menu_path, menu_parent):
        # default setting
        self.menu_parent = menu_parent
        self.menu_path = menu_path.replace("\\", "/")
        self._root_path = "maya_tools/tools/"
        self.this_module_str = self.menu_path.rsplit(self._root_path, 1)[-1]
        self.this_module_str = (self._root_path + self.this_module_str).replace("/", ".")

        # reload module
        menu_module = importlib.import_module(self.this_module_str)
        reload(menu_module)

        self.menu_setting_module = None
        self.load_menu_module()

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

        self.command = self.__get_menu_setting_attr("command") or None

    def __get_menu_setting_attr(self, attr_name):
        if not self.menu_setting_module:
            return None
        else:
            if hasattr(self.menu_setting_module, attr_name):
                return getattr(self.menu_setting_module, attr_name)
            else:
                return None

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

        print("--------------------")
        print(self.menu_type)
        print(self.object_name)
        print(self.label)
        print(self.menu_parent)
        print("--------------------")

        if self.menu_type.lower() == "menu":
            cmds.menu(self.object_name,
                      label=self.label,
                      parent=self.menu_parent,
                      tearOff=self.tearOff)

        elif self.menu_type.lower() == "submenu":
            cmds.menuItem(self.object_name,
                          subMenu=True,
                          label=self.label,
                          parent=self.menu_parent,
                          tearOff=self.tearOff)

        elif self.menu_type.lower() == "menuitem":
            # ../maya_tools/tools/WTools/ANI --> maya_tools.tools.WTools.ANI.menu
            cmd = 'print(u"There is no command set for [%s]")' % self.label

            if self.command:
                if self.command.startswith("{this_module}"):
                    self.command = self.command.format(this_module=self.this_module_str)

                parent_module = self.command.rsplit(".", 1)[0]
                exec_module = self.command.rsplit(".", 1)[-1]

                cmd = "import {};reload({});{}".format(parent_module,
                                                       parent_module,
                                                       parent_module + "." + exec_module)

            cmds.menuItem(self.object_name,
                          label=self.label,
                          parent=self.menu_parent,
                          tearOff=self.tearOff,
                          command=cmd)


def reload_scripts():
    import maya_tools.utils.reset_session_for_script as reset_session_for_script
    reload(reset_session_for_script)
    reset_session_for_script.reset(root_path=menu_path_root)


def build_menu(menu_path=menu_path_root,
               menu_parent="MayaWindow"):
    """
    build maya menu
    :return:
    """
    reload_scripts()

    # menu_obj = None
    for f in os.listdir(menu_path):
        if f.startswith("__"):  # ignore __init__, __pycache__
            continue

        f_path = os.path.join(menu_path, f).replace("\\", "/")
        if os.path.isdir(f_path):
            # menu_path = .../maya_tools/tools/WTools
            print("f_path: ", f_path, menu_parent)
            menu_obj = MenuObject(f_path, menu_parent)
            menu_obj.create_menu()

            if menu_obj.menu_type != "menuItem":
                build_menu(menu_path=f_path,
                           menu_parent=menu_obj.object_name)
    # if menu_obj:
    #     # build reload btn
    #     if menu_parent == 'MayaWindow':
    #         cmd = "import maya_tools.utils.reset_session_for_script as reset_session_for_script;"
    #         cmd += "reload(reset_session_for_script); reset_session_for_script.reset()"
    #         cmds.menuItem(menu_obj.object_name + '_reload',
    #                       label=u'重置菜单',
    #                       parent=menu_obj.object_name,
    #                       command=cmd)
    #
