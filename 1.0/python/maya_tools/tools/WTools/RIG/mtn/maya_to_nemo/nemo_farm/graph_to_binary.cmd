@echo off
call Y:\pipeline_studio\config\base_env_dev.bat

cd /d %~dp0

rez-env python-3 requests -- python %cd%\graph_to_binary.py %*