@echo off
echo ========================================
echo Breast Cancer AI System - PyTorch Setup
echo ========================================
echo.

echo Installing PyTorch for Windows...
echo This may take a few minutes...
echo.

REM Install PyTorch CPU version
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo Installation Successful!
    echo ========================================
    echo.
    echo PyTorch has been installed successfully.
    echo You can now use the image analysis feature.
    echo.
    echo To start the server:
    echo   python manage.py runserver
    echo.
    echo To access image analysis:
    echo   http://127.0.0.1:8000/image-predict/
    echo.
) else (
    echo.
    echo ========================================
    echo Installation Failed!
    echo ========================================
    echo.
    echo Please try manual installation:
    echo   pip install torch torchvision
    echo.
)

pause
