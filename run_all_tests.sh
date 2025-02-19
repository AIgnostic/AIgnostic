#!/bin/bash

concurrent=false

# Parse command line options
while getopts "c" opt; do
    case $opt in
        c)
            concurrent=true
            ;;
        *)
            echo "Usage: $0 [-c]"
            exit 1
            ;;
    esac
done

for dirname in packages/*; do
        package_name=$(basename "$dirname")
        if [ "$concurrent" = true ]; then
                npx nx test $package_name --skip-nx-cache &
        else
                npx nx test $package_name --skip-nx-cache
        fi
done

# Wait for all background jobs to finish if concurrency is enabled
if [ "$concurrent" = true ]; then
        wait
fi