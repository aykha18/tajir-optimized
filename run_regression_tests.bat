@echo off
echo ========================================
echo Tajir POS - Regression Test Runner
echo ========================================
echo.

cd tests

if "%1"=="--list" (
    python run_regression_tests.py --list
) else if "%1"=="--check" (
    python run_regression_tests.py --check
) else if "%1"=="--verbose" (
    python run_regression_tests.py --verbose
) else if "%1"=="--category" (
    python run_regression_tests.py --category %2
) else if "%1"=="--test" (
    python run_regression_tests.py --test %2
) else (
    echo Running complete regression test suite...
    python run_regression_tests.py
)

echo.
echo ========================================
echo Test execution completed.
echo ========================================
pause
