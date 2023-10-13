#!/bin/bash

error_catching() {
# check if the user inputs is valid 
    cd "$1" > /dev/null 2>&1
    if [[ $? != 0 ]]; then
        echo "Error: No such souce directory"
        return 1
    fi
    cd "$2" > /dev/null 2>&1
    if [[ $? != 0 ]]; then
        echo "Error: No such destination directory"
        return 1
    fi
    return 0
}

copy () {
    # from the source dir find all files matching the given pattern 
    # then copying it to des dir
    error_catching "$1" "$2"
    if [[ $? == 1 ]]; then
        return
    fi

    cd "$1"
    for FILE in $(ls -p | grep -v /); do
        if [[ "$FILE" == $3 ]]; then 
            cp "$FILE" "$2"
        fi
    done
}

# read inputs from user
read -p "Enter source directory: " src
read -p "Enter destination directory: " des
read -p "Enter pattern: " pattern

if [ -n "$src" -a -n "$des" -a -n "$pattern" ]; then
    copy "$src" "$des" "$pattern"
else
    echo "Error: Missing some argument"
fi



