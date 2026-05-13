@echo off
chcp 65001 >nul 2>&1
title All-to-All Converter
python "%~dp0run.py"
pause
