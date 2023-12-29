@echo off
call Y:\pipeline_studio\config\base_env.bat

rez-env python-3 requests -- python %~dp0\graph_to_binary.py %*