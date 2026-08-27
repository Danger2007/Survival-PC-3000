@REM port the shell script to Windows batch script

if not exist init.bat (
    echo Error: init.bat not found. Please run this script from the project root directory.
    exit /b 1
)
set SECRET_FILE=modules\settings_secrets.py

if not exist modules\cpp\build mkdir modules\cpp\build
cmake -G "Visual Studio 17 2022" -A x64 -S modules\cpp -B modules\cpp\build
cmake --build modules\cpp\build --config Release
copy modules\cpp\build\Release\* modules\cpp\


if not exist %SECRET_FILE% (
    type nul > %SECRET_FILE%
    set /p REAL_LOCATION=Please enter your REAL_LOCATION (e.g., 'New York'): 
    set /p LONGITUDE=Please enter your LONGITUDE (e.g., '-74.0060'): 
    set /p LATITUDE=Please enter your LATITUDE (e.g., '40.7128'): 
    set /p GEOAPIFY_API_KEY=Please enter your GEOAPIFY_API_KEY (get one for free at https://www.geoapify.com): 

    echo REAL_LOCATION='%REAL_LOCATION%' >> %SECRET_FILE%
    echo LONGITUDE='%LONGITUDE%' >> %SECRET_FILE%
    echo LATITUDE='%LATITUDE%' >> %SECRET_FILE%
    echo GEOAPIFY_API_KEY='%GEOAPIFY_API_KEY%' >> %SECRET_FILE%
)

