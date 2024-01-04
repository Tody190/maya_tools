#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/1/3 18:46
# @Author  : YangTao


import maya.cmds as cmds


class CallbackObject(object):
    def __init__(self):
        self.scene_message = None

    def callback_fun(self):
        pass


class EvaluationManagerMode(CallbackObject):  # off, on, all
    def __init__(self):
        super(EvaluationManagerMode, self).__init__()
        self.scene_message = None

# def set_evaluation_manager_mode():
#     # when render with 'xgen', the hair will not work
#     # set evaluation manager mode 'off' can fix this problem
#     # so, when you want to set the evaluation manager mode 'off'
#     # add environment variable YT_MAYA_EVALUATION_MANAGER_MODE='off'
