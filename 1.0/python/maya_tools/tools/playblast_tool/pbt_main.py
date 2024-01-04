#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/1/3 15:53
# @Author  : YangTao


import maya.cmds as cmds

# default value



class PlayBlastCore(object):
    def __init__(self, camera_name, output_file, **kwargs):
        """
        :param camera_name:
        :param output_file:
        :param width : image width
        :param height : image height
        """
        self.camera = cmds.ls(camera_name, long=True)[0]
        self.output_file = output_file

        self.width = kwargs.get('width') or cmds.getAttr('defaultResolution.width')
        self.height = kwargs.get('height') or cmds.getAttr('defaultResolution.height')

        self.start_time = kwargs.get('start_f') or cmds.playbackOptions(q=True, minTime=True)
        self.end_time = kwargs.get('end_f') or cmds.playbackOptions(q=True, maxTime=True)


    def start_play_blast(self):
        cmds.playblast(filename=self.output_file,
                     fmt='image',
                     compression='tif',

                     width=self.width,
                     height=self.height,

                     startTime=self.start_time,
                     endTime=self.end_time,
                     framePadding=4,

                     percent=100,
                     quality=100,

                     viewer=False,
                     offScreen=True,
                     clearCache=True,
                     showOrnaments=False,
                     forceOverwrite=True)