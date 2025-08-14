@echo off
setlocal
REM Rendre le layout src/ visible pour Python
set "PYTHONPATH=%CD%\src"

REM Activer le venv si dispo
IF EXIST ".venv\Scripts\activate.bat" call ".venv\Scripts\activate.bat"

REM Appeler directement les ex?cutables du venv
".\.venv\Scripts\ruff.exe" check src tests || exit /b %errorlevel%
".\.venv\Scripts\black.exe" src tests     || exit /b %errorlevel%
".\.venv\Scripts\pytest.exe"
