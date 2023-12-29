#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/29 15:41
# @Author  : YangTao

import os
import re
import traceback

from PySide2.QtWidgets import QWidget
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QHBoxLayout
from PySide2.QtWidgets import QTableWidget
from PySide2.QtWidgets import QTableWidgetItem
from PySide2.QtWidgets import QHeaderView
from PySide2.QtWidgets import QPushButton
from PySide2.QtWidgets import QLabel
from PySide2.QtCore import Qt

import maya.cmds as cmds
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin


class RigAssetInfo:
    def __init__(self, reference_node):
        self.ref_node = reference_node
        self.ref_namespace = cmds.referenceQuery(self.ref_node, namespace=True)
        self.maya_file_path = cmds.referenceQuery(self.ref_node, filename=1).replace("\\", "/")
        self.maya_file_path  = re.sub(re.compile(r'\{\d+\}$'),
                                      '',
                                      self.maya_file_path )

        self.file_name = os.path.basename(self.maya_file_path)
        self.asset_name = os.path.splitext(self.file_name)[0]  # text_cg_v04_c001001ld_hi_rig
        self.project_name = self.maya_file_path.split("/")[2]  # TEXT_CG_v04
        self.file_type = self.maya_file_path.split("/")[3]  # asset or shot
        self.entity_type = self.maya_file_path.split("/")[4]  # Character or Props or Set ....
        self.entity_name = self.maya_file_path.split("/")[5]  # c001001ld
        self.pipeline_type = self.maya_file_path.split("/")[6]  # rig or rig_nemo

        self.is_rig_asset = True
        if self.file_type not in ['asset', 'asset_work']:
            self.is_rig_asset = False

        if self.pipeline_type not in ['rig', 'rig_nemo']:
            self.is_rig_asset = False

    @property
    def nemo_rig_file(self):
        if self.is_rig_asset:
            # compatible with both cases
            # Z:\cgteamwork7\P5\asset_work\Character\C002_A_00\rig\lo\ok\P5_C001_A_00_hi_rig.mb
            # Z:\cgteamwork7\P5\asset\Character\C001_A_00\rig\P5_C001_A_00_hi_rig.mb
            return self.maya_file_path.replace('/{}/rig/'.format(self.entity_name),
                                               '/{}/rig_nemo/'.format(self.entity_name))

    @property
    def maya_rig_file(self):
        if self.is_rig_asset:
            return self.maya_file_path.replace('/{}/rig_nemo/'.format(self.entity_name),
                                               '/{}/rig/'.format(self.entity_name))

    def switch_to_nemo(self):
        if self.pipeline_type == 'rig' and os.path.exists(self.nemo_rig_file):
            cmds.file(self.nemo_rig_file,
                      loadReference=self.ref_node)

    def switch_to_maya(self):
        if self.pipeline_type == 'rig_nemo' and os.path.exists(self.maya_rig_file):
            cmds.file(self.maya_rig_file,
                      loadReference=self.ref_node)

class SwitchUI(MayaQWidgetDockableMixin, QWidget):
    INSTANCE = None
    def __init__(self, parent=None):
        super(SwitchUI, self).__init__(parent)
        self.setWindowTitle("Nemo Rig Switcher")
        self.setObjectName("SwitchUI")
        self.setMinimumWidth(400)

        msg = u'只有引用且符合项目路径规范的资产会显示在下面的表格中\n'
        msg += u'点击按钮切换绑定类型'

        self.info_label = QLabel(msg)

        self.table_widget = QTableWidget(self)
        self.table_widget.setFocusPolicy(Qt.NoFocus)
        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels(["资产名", "当前绑定状态", "是否有nemo绑定"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.switch_maya_rig = QPushButton(u'切换为 Maya Rig')
        self.switch_nemo_rig = QPushButton(u'切换为 Nemo Rig')

        self.switch_maya_rig.clicked.connect(self.switch_to_maya)
        self.switch_nemo_rig.clicked.connect(self.switch_to_nemo)

        layout = QVBoxLayout(self)
        layout.addWidget(self.info_label)
        layout.addWidget(self.table_widget)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.switch_maya_rig)
        btn_layout.addWidget(self.switch_nemo_rig)
        layout.addLayout(btn_layout)

        self.rig_assets_obj = []

    def set_rig_assets(self, rig_assets):
        self.rig_assets_obj = rig_assets

        self.table_widget.setRowCount(len(self.rig_assets_obj))

        row = 0
        for rai in self.rig_assets_obj:
            self.set_table_cell_value(0, 0, str(rai.ref_namespace))

            if rai.pipeline_type == 'rig':
                self.set_table_cell_value(0, 1, 'Maya Rig')
            if rai.pipeline_type == 'rig_nemo':
                self.set_table_cell_value(0, 1, 'Nemo Rig')

            if os.path.isfile(rai.nemo_rig_file):
                self.set_table_cell_value(0, 2, 'Yes')
            else:
                self.set_table_cell_value(0, 2, 'No')
            row += 1

    def set_table_cell_value(self, row, col, value):
        item = QTableWidgetItem(str(value))
        item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.table_widget.setItem(row, col, item)

    def switch_to_nemo(self):
        for rai in self.rig_assets_obj:
            rai.switch_to_nemo()
        self.close()

    def switch_to_maya(self):
        for rai in self.rig_assets_obj:
            rai.switch_to_maya()
        self.close()


def switch():
    sel_nodes = cmds.ls(sl=1)

    if not sel_nodes:
        cmds.confirmDialog(title=u'没选中任何物体',
                           message=u'至少在场景中选中一个引用资产（任意部分）',
                           icon='warning')
        return

    ref_node_list = []
    for n in sel_nodes:
        ref_node = cmds.referenceQuery(n, referenceNode=1)
        if ref_node not in ref_node_list:
            ref_node_list.append(ref_node)

    rig_assets_info = []
    for n in ref_node_list:
        try:
            rai = RigAssetInfo(n)
            rig_assets_info.append(rai)
        except:
            print(traceback.print_exc())

    if not rig_assets_info:
        msg = u'选中的资产必须是引用资产，且在项目的绑定路径下\n'
        msg += u'当前选中的都不符合规范'
        cmds.confirmDialog(title=u'没有符合规范的资产',
                           message=msg,
                           icon='warning')
        return
    else:
        if SwitchUI.INSTANCE:
            SwitchUI.INSTANCE.close()
        else:
            SwitchUI.INSTANCE = SwitchUI()

        # add rows
        SwitchUI.INSTANCE.set_rig_assets(rig_assets_info)
        SwitchUI.INSTANCE.set_table_cell_value(0, 0, '资产名')
        SwitchUI.INSTANCE.show()


