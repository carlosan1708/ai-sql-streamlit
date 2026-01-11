#!/bin/bash

# Define the target file
INIT_FILE="init.sql"
URL="https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_PostgreSql.sql"

# Check if init.sql exists
if [ ! -f "$INIT_FILE" ]; then
    echo "$INIT_FILE not found. Downloading from $URL..."
    curl -s -o "$INIT_FILE" "$URL"
    if [ $? -eq 0 ]; then
        echo "Download successful."
    else
        echo "Error: Failed to download $INIT_FILE."
        exit 1
    fi
else
    echo "$INIT_FILE already exists. Skipping download."
fi
