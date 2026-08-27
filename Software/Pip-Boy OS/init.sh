#!/bin/bash

SECRET_FILE="modules/settings_secrets.py"

# if current directory is not project root (contains init.sh), exit with error
if [ ! -f init.sh ]; then
    echo "Error: init.sh not found. Please run this script from the project root directory."
    exit 1
fi

# Build script for modules/cpp using CMake (Linux/macOS version)

# Create build directory if it doesn't exist
mkdir -p modules/cpp/build

# Generate build files
cmake -S modules/cpp -B modules/cpp/build

# Build the project (Release mode)
cmake --build modules/cpp/build --config Release

# Copy built files from Release to modules/cpp (if Release dir exists)
if [ -d modules/cpp/build/Release ]; then
    cp modules/cpp/build/Release/* modules/cpp/
fi


# Create settings_secrets.py if it doesn't exist
if [ ! -f $SECRET_FILE ]; then
    touch $SECRET_FILE
    # create REAL_LOCATION, LONGITUDE, LATITUDE GEOAPIFY_API_KEY variables in settings_secrets.py using user input
    echo "Please enter your REAL_LOCATION (e.g., 'New York'):"
    read REAL_LOCATION
    echo "Please enter your LONGITUDE (e.g., '-74.0060'):"
    read LONGITUDE
    echo "Please enter your LATITUDE (e.g., '40.7128'):"
    read LATITUDE
    echo "Please enter your GEOAPIFY_API_KEY (get one for free at https://www.geoapify.com):"
    read GEOAPIFY_API_KEY 

    echo "REAL_LOCATION='$REAL_LOCATION'" >> $SECRET_FILE
    echo "LONGITUDE='$LONGITUDE'" >> $SECRET_FILE
    echo "LATITUDE='$LATITUDE'" >> $SECRET_FILE
    echo "GEOAPIFY_API_KEY='$GEOAPIFY_API_KEY'" >> $SECRET_FILE


fi


