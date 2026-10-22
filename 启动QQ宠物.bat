@echo off
setlocal
title QQ Pet Launcher

set "APP_DIR=%~dp0qq-pet-macos"
set "ELECTRON=%APP_DIR%\node_modules\electron\dist\electron.exe"
set "LOG=%TEMP%\qqpet-launcher-%RANDOM%%RANDOM%.log"

if not exist "%APP_DIR%\package.json" (
  echo [ERROR] Game directory not found:
  echo   %APP_DIR%
  echo.
  echo Keep this script next to the qq-pet-macos directory.
  echo.
  pause
  exit /b 1
)

if not exist "%ELECTRON%" (
  echo [ERROR] Electron runtime not found:
  echo   %ELECTRON%
  echo.
  echo Install dependencies first:
  echo   cd /d "%APP_DIR%"
  echo   npm install
  echo.
  pause
  exit /b 1
)

rem If the game is already running, just bring the pet window to the front.
call :is_running
if not errorlevel 1 (
  echo.
  echo   QQ Pet is already running.
  echo   Bringing the pet window to the front...
  start "" /d "%APP_DIR%" "%ELECTRON%" "%APP_DIR%"
  ping -n 4 127.0.0.1 >nul
  exit /b 0
)

echo.
echo   Starting QQ Pet, please wait...
echo.

rem Use a unique log file per launch: a running instance holds its own log
rem handle, and a fixed name would make the next launch fail with
rem "the process cannot access the file because it is being used by another process".
start "" /d "%APP_DIR%" "%ELECTRON%" "%APP_DIR%" >"%LOG%" 2>&1
if errorlevel 1 (
  rem Redirection failed for some reason, start without a log.
  start "" /d "%APP_DIR%" "%ELECTRON%" "%APP_DIR%"
)

rem Wait up to ~20 seconds for our process to appear.
set "OK="
for /l %%i in (1,1,5) do (
  ping -n 4 127.0.0.1 >nul
  call :is_running
  if not errorlevel 1 (
    set "OK=1"
    goto :check
  )
)

:check
if not defined OK goto :failed

rem Give it a moment, then make sure it did not crash immediately.
ping -n 4 127.0.0.1 >nul
call :is_running
if errorlevel 1 goto :failed

echo   QQ Pet is running. This window will close in 2 seconds.
ping -n 3 127.0.0.1 >nul
exit /b 0

:failed
echo.
echo [ERROR] QQ Pet failed to start.
echo.
if exist "%LOG%" (
  echo ---- launcher log ----
  type "%LOG%"
  echo ----------------------
  echo Log file: %LOG%
) else (
  echo No log was written.
)
echo.
pause
exit /b 1

:is_running
powershell -NoProfile -Command "if (Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'electron.exe' -and $_.CommandLine -like '*qq-pet-macos*' }) { exit 0 } else { exit 1 }" >nul 2>&1
if errorlevel 1 exit /b 1
exit /b 0
