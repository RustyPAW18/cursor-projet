@echo off
IF EXIST .venv\Scripts\activate.bat call .venv\Scripts\activate.bat
ruff check src tests
