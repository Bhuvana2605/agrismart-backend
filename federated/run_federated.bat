@echo off
REM Federated Learning Quick Start Script for Windows
REM This script helps you start the server and clients easily

echo ========================================
echo Federated Learning - Crop Recommendation
echo ========================================
echo.

:menu
echo Choose an option:
echo 1. Start Server
echo 2. Start Client 0
echo 3. Start Client 1
echo 4. Start Client 2
echo 5. Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto server
if "%choice%"=="2" goto client0
if "%choice%"=="3" goto client1
if "%choice%"=="4" goto client2
if "%choice%"=="5" goto exit

echo Invalid choice. Please try again.
echo.
goto menu

:server
echo.
echo Starting Federated Learning Server...
echo.
python server.py
goto end

:client0
echo.
echo Starting Client 0...
echo.
python client.py 0
goto end

:client1
echo.
echo Starting Client 1...
echo.
python client.py 1
goto end

:client2
echo.
echo Starting Client 2...
echo.
python client.py 2
goto end

:exit
echo.
echo Exiting...
goto end

:end
pause
