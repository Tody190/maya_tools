# -*- coding: utf-8 -*-

name = 'maya_tools'

version = '1.0'

description = 'Maya tools for maya'

authors = ['YangTao']

requires = [
    'pub_auts',
    'nemo'
]


def commands():
    env.PYTHONPATH.prepend('{this.root}/python')
    env.MAYA_SCRIPT_PATH.prepend('{this.root}/python')


uuid = 'maya_tools'