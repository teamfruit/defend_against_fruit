@echo off
python %~dp0\ci_config\ci_bootstrap.py --run "%~dp0\ci_config\ci_run.py %*"