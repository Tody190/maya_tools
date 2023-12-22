# -*- coding: utf-8 -*-

name = 'maya_tools'

version = '1.0'

description = 'Maya tools for maya'

authors = ['YangTao']

requires = [
    'maya',
    'nemo'
]


def commands():
    env.PYTHONPATH.append('{this.root}/maya_to_nemo_menu')
    env.MAYA_SCRIPT_PATH.prepend('{this.root}/maya_to_nemo_menu')



uuid = 'maya_tools'