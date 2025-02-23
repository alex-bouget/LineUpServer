#!/bin/sh

for filename in /app/apk/*; do
    [ -e "$filename" ] || continue
    echo "Processing apk requirement $filename"
    while read -r line
    do
        echo "Installing $line"
        apk add --no-cache $line
    done < "$filename"
done
for filename in /app/pip/*; do
    [ -e "$filename" ] || continue
    echo "Processing pip requirement $filename"
    pip install -r $filename
done
for filename in /app/bash/*; do
    [ -e "$filename" ] || continue
    echo "Processing bash script $filename"
    chmod +x $filename
    source $filename
done
echo "Starting server"
python server.py