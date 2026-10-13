REM PhantomID — lightweight start reference (not a service or install)
REM Runs from project folder; creates profile DB in %LOCALAPPDATA%\PhantomID.
REM No hidden startup; user must choose to run. No admin required.
@echo off
if exist .\.venv\Scripts\python.exe (
    .\.venv\Scripts\python.exe -m phantomid
) else (
    python -m phantomid
)
