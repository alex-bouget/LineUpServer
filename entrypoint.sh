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

python -m fastapi run --port 80 --no-reload --no-proxy-headers