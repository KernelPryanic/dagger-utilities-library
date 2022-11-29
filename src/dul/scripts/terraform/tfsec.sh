#!/bin/bash

while getopts ":d:" opt; do
    case $opt in
    d)
        DIRECTORY=$OPTARG
        ;;
    \?)
        echo "Invalid option: -$OPTARG" >&2
        exit 1
        ;;
    :)
        echo "Option -$OPTARG requires an argument." >&2
        exit 1
        ;;
    esac
done

MAINS=$(find $DIRECTORY -type f -name "main.tf" | sed 's/[^\/]*$//g')

while IFS= read -r project; do
    set +e
    tfsec "${project}"
    set -e
    tmp_rc=$?
    RC=$((RC > tmp_rc ? RC : tmp_rc))
done <<<"$PROJECTS"

if [[ "$RC" -eq 0 ]]; then
    echo "✨ 🍰 ✨ tfsec code check passed"
else
    echo "💥 💔 💥 tfsec code check failed."
    exit 1
fi
