#!/usr/bin/env maya_to_nemo_menu
# -*- coding: utf-8 -*-
# @Time    : 2023/12/20 13:44
# @Author  : YangTao
# @File    : maya_rig_to_nemo_rig

import os
import requests
import time
import shutil
import re

import maya.cmds as cmds

from nemo.n2m import n2m
from nemo.m2n import m2n
from nemo.filter import scene_collect


def check_and_load_plugin(plugin_name):
    if cmds.pluginInfo(plugin_name, query=True, loaded=True):
        return True

    try:
        cmds.loadPlugin(plugin_name)
        return True
    except Exception as e:
        msg = u'Nemo 插件加载失败\n'
        msg += str(e)
        cmds.confirmDialog(title=u'失败',
                           message=msg,
                           icon='critical')
        return False


class RigAssetInfo:
    def __init__(self, maya_file_path):
        self.maya_file_path = maya_file_path.replace("\\", "/")
        self.file_name = os.path.basename(self.maya_file_path)
        self.asset_name = os.path.splitext(self.file_name)[0]  # text_cg_v04_c001001ld_hi_rig
        self.project_name = self.maya_file_path.split("/")[2]  # TEXT_CG_v04
        self.file_type = self.maya_file_path.split("/")[3]  # asset or shot
        self.entity_type = self.maya_file_path.split("/")[4]  # Character or Props or Set ....
        self.entity_name = self.maya_file_path.split("/")[5]  # c001001ld
        self.pipeline_type = self.maya_file_path.split("/")[6]  # rig

        if self.file_type not in ['asset', 'asset_work']:
            self.comply_with_asset_specifications = False
            msg = u'只支持 asset 类型的资产，当前文件类型为 %s \n' % self.file_type
            raise ValueError(msg)

    @property
    def nemo_root_path(self):
        # compatible with both cases
        # Z:\cgteamwork7\P5\asset_work\Character\C002_A_00\rig\lo\ok\P5_C001_A_00_hi_rig.mb
        # Z:\cgteamwork7\P5\asset\Character\C001_A_00\rig\P5_C001_A_00_hi_rig.mb
        dir_path = os.path.dirname(self.maya_file_path)
        return dir_path.replace('/{}/rig'.format(self.entity_name),
                                '/{}/rig_nemo'.format(self.entity_name))

    @property
    def nemo_rig_file(self):
        return self.nemo_root_path + '/{}'.format(self.file_name)

    @property
    def nemo_data_path(self):
        return self.nemo_root_path + '/nemodata'

    @property
    def nemo_export_path(self):
        return self.nemo_root_path + '/nemoexport'


def go():
    # get maya file path
    src_file = cmds.file(query=True, sn=True)
    if not src_file:
        cmds.confirmDialog(title=u'失败',
                           message=u'没有打开任何maya文件',
                           icon='critical')
        return
    else:
        src_file = src_file.replace('\\', '/')

    # check asset info
    try:
        asset_info = RigAssetInfo(src_file)
    except Exception as e:
        msg = u'此文件不符合项目规范，只接受符合以下路径格式的资产\n'
        msg += u'Z:/cgteamwork7/{项目名}/asset/{资产类型}/{资产名}/rig/%s\n' % os.path.basename(src_file)
        msg += u'or\n'
        msg += u'Z:/cgteamwork7/{项目名}/asset_work/{资产类型}/{资产名}/rig/lo/ok/%s\n' % os.path.basename(src_file)
        msg += str(e)
        cmds.confirmDialog(title=u'失败',
                           message=msg,
                           icon='critical')
        print(e)
        return

    # check and laod maya
    if not check_and_load_plugin("Nemo.mll"):
        return

    # check whether you can log in to the nemo farm

    if not os.path.exists(asset_info.nemo_root_path):
        os.makedirs(asset_info.nemo_root_path)  # make nemo file path
    if not os.path.exists(asset_info.nemo_data_path):
        os.makedirs(asset_info.nemo_data_path)  # make nemodata path
    if not os.path.exists(asset_info.nemo_export_path):
        os.makedirs(asset_info.nemo_export_path)  # make nemodata path

    controllers = scene_collect.get_controllers(patterns=['*'], curve=True, ui=True)
    shapes = scene_collect.get_meshes(['|'], controllers)

    # export nemo __GRAPH.json and __EXPORT.zip
    graph_json, export_zip = m2n.export(identifier=asset_info.asset_name,
                                        controllers=controllers,
                                        shapes=shapes,
                                        material=True,
                                        project_dir=asset_info.nemo_export_path,
                                        overwrite=True)

    if not os.path.exists(graph_json) or not os.path.exists(export_zip):
        cmds.confirmDialog(title=u'失败',
                           message=u'无法导出__GRAPH.json 和 __EXPORT.zip',
                           icon='critical')
        return

    # Graph to Binary
    # upload and download __GRAPH.json
    binary_zip = asset_info.nemo_export_path
    binary_zip += '/' + os.path.basename(graph_json).replace('__GRAPH.json', '__BINARY.zip')
    if os.path.isfile(binary_zip):
        os.remove(binary_zip)

    graph_to_binary_cmd = os.path.dirname(__file__).replace('\\', '/')
    graph_to_binary_cmd += '/nemo_farm/graph_to_binary.cmd'
    command = '{0} {1} {2}'.format(graph_to_binary_cmd, graph_json, asset_info.nemo_export_path)
    os.system(command)

    if not os.path.isfile(export_zip) or not os.path.isfile(binary_zip):
        msg = u'在 {} 下无法找到 __EXPORT.zip 和 __BINARY.zip'.format(asset_info.nemo_export_path)
        cmds.confirmDialog(title=u'失败',
                           message=msg,
                           icon='critical')
        return

    # export_zip = "C:/nemo_temp/rig_nemo/nemoexport/text_cg_v04_c001001ld_hi_rig__EXPORT.zip"
    # binary_zip = "C:/nemo_temp/rig_nemo/nemoexport/text_cg_v04_c001001ld_hi_rig__BINARY.zip"
    # assembler nemo
    n2m.assemble(str(export_zip),
                 str(binary_zip),
                 asset_info.nemo_root_path,
                 dir_data=asset_info.nemo_data_path,
                 relative_path=True,
                 headless=False,
                 ctrl_proxy=False)

    if os.path.isfile(asset_info.nemo_rig_file):
        cmds.confirmDialog(title=u'Enjoy it!',
                           message=u'转换完成，文件在\n{}'.format(asset_info.nemo_rig_file),
                           icon='information')
    else:
        cmds.confirmDialog(title=u'失败',
                           message=u'转换失败',
                           icon='critical')
