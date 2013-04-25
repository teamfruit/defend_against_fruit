@echo off
python %~dp0\fruit_orchard\fruit_orchard\virtualenv_util.py ^
    --cfg_file="%~dp0\ci_config\virtualenv_util.cfg" ^
    --run "%~dp0\ci_config\ci_run.py %*"