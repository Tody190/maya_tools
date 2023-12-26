#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/25 13:54
# @Author  : YangTao
from __future__ import print_function

import inspect
import sys


def reset(root_path):
    # Convert this to lower just for a clean comparison later
    root_path = root_path.lower()

    to_delete = []
    # Iterate over all the modules that are currently loaded
    for key, module in sys.modules.items():
        # There's a few modules that are going to complain if you try to query them
        # so I've popped this into a try/except to keep it safe
        try:
            # Use the "inspect" library to get the module_file_path that the current module was loaded from
            module_file_path = inspect.getfile(module).lower()
            # # Don't try and remove the startup script, that will break everything
            # if module_file_path == __file__.lower():
            #     continue

            # If the module's filepath contains the userPath, add it to the list of modules to delete
            if module_file_path.startswith(root_path):
                print("Removing %s" % key)
                to_delete.append(key)
        except:
            pass

    # If we'd deleted the module in the loop above, it would have changed the size of the dictionary and
    # broken the loop. So now we go over the list we made and delete all the modules
    for module in to_delete:
        del (sys.modules[module])
