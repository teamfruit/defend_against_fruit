@echo off
python %~dp0\daf_fruit_orchard\daf_fruit_orchard\virtualenv_util.py ^
    --cfg_file="%~dp0\ci_config\virtualenv_util.cfg" ^
    --run "%~dp0\ci_config\ci_run.py %*"