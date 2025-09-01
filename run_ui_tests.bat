@echo off
echo ============================================================
echo TAJIR POS - UI TEST RUNNER
echo ============================================================
echo.

echo Installing UI testing requirements...
python -m pip install -r tests/requirements_ui.txt

if %ERRORLEVEL% NEQ 0 (
    echo Failed to install requirements
    pause
    exit /b 1
)

echo.
echo Running UI tests...
python run_ui_tests.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo UI tests failed!
    pause
    exit /b 1
) else (
    echo.
    echo UI tests completed successfully!
)

pause
