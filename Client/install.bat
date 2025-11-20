@echo off
setlocal

REM --- Paths ---
set APP_DIR=C:\Program Files\ScreenshotClient
set EXE_PATH=%APP_DIR%\client.exe
set INI_PATH=%APP_DIR%\options.ini
set TASK_XML=%APP_DIR%\ScreenshotClient.xml

set SOURCE_EXE=\\dc-1\install\GPO\monitor\client.exe
set SOURCE_INI=\\dc-1\install\GPO\monitor\options.ini

REM --- Create program folder if missing ---
if not exist "%APP_DIR%" (
    mkdir "%APP_DIR%"
)

REM --- Copy executable ---
copy "%SOURCE_EXE%" "%APP_DIR%\" /Y

REM --- Copy INI ---
copy "%SOURCE_INI%" "%APP_DIR%\" /Y

REM --- Create Scheduled Task XML ---
(
echo ^<?xml version="1.0" encoding="UTF-16"?^>
echo ^<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task"^>
echo   ^<RegistrationInfo^>
echo     ^<Description^>Launch Screenshot Client for any logged-in user.^</Description^>
echo   ^</RegistrationInfo^>
echo   ^<Triggers^>
echo     ^<LogonTrigger^>
echo       ^<Enabled^>true^</Enabled^>
echo     ^</LogonTrigger^>
echo   ^</Triggers^>
echo   ^<Principals^>
echo     ^<Principal id="AnyUser"^>
echo       ^<LogonType^>InteractiveToken^</LogonType^>
echo       ^<RunLevel^>LeastPrivilege^</RunLevel^>
echo     ^</Principal^>
echo   ^</Principals^>
echo   ^<Settings^>
echo     ^<MultipleInstancesPolicy^>IgnoreNew^</MultipleInstancesPolicy^>
echo     ^<StartWhenAvailable^>true^</StartWhenAvailable^>
echo     ^<Enabled^>true^</Enabled^>
echo     ^<Hidden^>true^</Hidden^>
echo   ^</Settings^>
echo   ^<Actions Context="AnyUser"^>
echo     ^<Exec^>
echo       ^<Command^>%EXE_PATH%^</Command^>
echo       ^<WorkingDirectory^>%APP_DIR%^</WorkingDirectory^>
echo     ^</Exec^>
echo   ^</Actions^>
echo ^</Task^>
) > "%TASK_XML%"

REM --- Delete existing task ---
schtasks /delete /tn ScreenshotClient /f >nul 2>&1

REM --- Create scheduled task for ALL users ---
schtasks /create /tn ScreenshotClient /xml "%TASK_XML%" /f

endlocal
exit /b 0
