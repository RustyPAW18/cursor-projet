@echo off
IF EXIST .venv\Scripts\activate.bat call .venv\Scripts\activate.bat
pytest
