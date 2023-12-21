#!/usr/bin/env maya_to_nemo_menu
# -*- coding: utf-8 -*-
# @Time    : 2023/12/20 11:30
# @Author  : YangTao
# @File    : startup.py


import importlib
import os
import platform

if platform.python_version().split(".")[0] == "3":
    reload = importlib.reload

import pymel.core as pm

root_dir_name = "tools"
menu_path_root = os.path.dirname(__file__) + "/" + root_dir_name


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
            if f == "menu.py":
                # ../maya_tools/tools/WTools/ANI --> maya_tools.tools.WTools.ANI.menu
                module_name ="{}.{}.{}".format(root_dir_name,
                                            self.menu_path.split("/{}/".format(root_dir_name), 1)[-1].replace("/", "."),
                                               "menu")

                self.menu_module = importlib.import_module(module_name)
                reload(self.menu_module)

    def create_menu(self):
        # rebuild the main menu
        if pm.menu(self.object_name, exists=True):
            pm.deleteUI(self.object_name, menu=True)

        if self.menu_type == "menu":
            pm.menu(self.object_name,
                    label=self.label,
                    parent=self.menu_parent,
                    tearOff=self.tearOff)

        elif self.menu_type == "subMenu":
            pm.menuItem(self.object_name,
                        subMenu=True,
                        label=self.label,
                        parent=self.menu_parent,
                        tearOff=self.tearOff)

        elif self.menu_type == "menuItem":
            pm.menuItem(self.object_name,
                        label=self.label,
                        parent=self.menu_parent,
                        tearOff=self.tearOff)


def build_menu(menu_path=menu_path_root,
               menu_parent="MayaWindow"):
    """
    build maya menu
    :return:
    """
    for f in os.listdir(menu_path):
        f_path = os.path.join(menu_path, f).replace("\\", "/")
        if os.path.isdir(f_path):
            # menu_path = .../maya_tools/tools/WTools
            menu_obj = MenuObject(f_path, menu_parent)
            menu_obj.create_menu()

            if menu_obj.menu_type != "menuItem":
                print(f_path)
                print(menu_obj.menu_type)
                build_menu(menu_path=f_path,
                           menu_parent=menu_obj.object_name)

        #
        # for name in files:
        #     print(name)

    print("** build maya menu **")
