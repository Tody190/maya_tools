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

script_file_name = os.path.basename(__file__)

def check_and_load_plugin(plugin_name):
    if cmds.pluginInfo(plugin_name, query=True, loaded=True):
        return True

    try:
        cmds.loadPlugin(plugin_name)
        return True
    except Exception as e:
        msg = u'Nemo 插件加载失败\n'
        msg += str(e)
        cmds.confirmDialog(title=script_file_name,
                           message=msg,
                           icon='critical')
        return False


class RigAssetInfo:
    def __init__(self, maya_file_path):
        self.file_name = os.path.basename(maya_file_path)
        self.asset_name = os.path.splitext(self.file_name)[0]  # text_cg_v04_c001001ld_hi_rig
        self.project_name = maya_file_path.split("/")[2]  # TEXT_CG_v04
        self.file_type = maya_file_path.split("/")[3]  # asset or shot
        self.entity_type = maya_file_path.split("/")[4]  # Character or Props or Set ....
        self.entity_name = maya_file_path.split("/")[5]  # c001001ld
        self.pipeline_type = maya_file_path.split("/")[6]  # rig

        if self.file_type != 'asset':
            self.comply_with_asset_specifications = False
            msg = u'只支持 asset 类型的资产，当前文件类型为 %s \n' % self.file_type
            cmds.confirmDialog(title=script_file_name,
                               message=u'此文件不符合项目规范\n',
                               icon='critical')
            raise ValueError(msg)

    @property
    def nemo_root_path(self):
        return 'Z:/cgteamwork7/{project_name}/asset/{entity_type}/{entity_name}/rig_nemo'.format(
            project_name=self.project_name,
            entity_type=self.entity_type,
            entity_name=self.entity_name,
        )

    @property
    def nemo_rig_file(self):
        return self.nemo_root_path + '/{}'.format(self.file_name)

    @property
    def nemo_data_path(self):
        return self.nemo_root_path + '/nemodata'


def nemo_farm_conversion(auth, graph_json):
    url = "https://www.nemopuppet.com/api"
    message = {
        'username': 'toddyyoung',
        'password': 'NP#yt@10',
    }

    recv = requests.post(url + '/login', data=message)
    auth = recv.cookies

    files = {'file': open(graph_json, 'rb')}
    message = {'platform': 'Windows', 'gpu': True}
    recv = requests.post(url + '/tasks', data=message, files=files, cookies=auth)
    task_id = recv.json()['id']

    while True:
        recv = requests.get('{}/task/{}'.format(url, task_id), cookies=auth)
        task_status = recv.json()['status']
        print(task_status)
        if task_status in {'Waiting', 'Running'}:
            time.sleep(5)
        else:
            break

    if task_status == 'Success':
        recv = requests.get(url + '/artifact/{}'.format(task_id), stream=True, cookies=auth)
        filename = re.findall('filename=\"(.+)\"', recv.headers['content-disposition'])[0]

        with open('<BinaryZipFolder>/{}'.format(filename), 'wb') as f:
            shutil.copyfileobj(recv.raw, f)


def go():
    # get maya file path
    src_file = cmds.file(query=True, sn=True)
    if not src_file:
        cmds.confirmDialog(title=script_file_name,
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
        msg += str(e)
        cmds.confirmDialog(title=script_file_name,
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

    from nemo.m2n import m2n
    from nemo.filter import scene_collect

    controllers = scene_collect.get_controllers(patterns=['*'], curve=True, ui=True)
    shapes = scene_collect.get_meshes(['|'], controllers)

    # export nemo __GRAPH.json and __EXPORT.zip
    graph_json, export_zip = m2n.export(identifier=asset_info.asset_name,
                                         controllers=controllers,
                                         shapes=shapes,
                                         project_dir=asset_info.nemo_data_path)

    if not os.path.exists(graph_json) or not os.path.exists(export_zip):
        cmds.confirmDialog(title=script_file_name,
                           message=u'导出__GRAPH.json 和 __EXPORT.zip 失败',
                           icon='critical')
        return

    # upload and download BINARY.zip

    # assembler nemo

    pass
