#!/bin/bash

while getopts ":d:l" opt; do
    case $opt in
    d)
        DIRECTORY=$OPTARG
        ;;
    l)
        LOCAL=true
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

MAINS=$(find $DIRECTORY -type f -name "main.tf")
RC=0

while IFS= read -r main; do
    readme=$(echo "$main" | sed -e 's/main.tf$/README.md/g')
    dir=$(dirname "$main")

    if [[ $LOCAL == true ]]; then
        echo "Updating/generating $readme"
        terraform-docs markdown table --output-file README.md --output-mode inject "$dir"
    else
        if [[ ! -f "$readme" ]]; then
            echo "💣 README $readme doesn't exists."
            echo "Try running 'terraform-docs markdown table --output-file README.md --output-mode inject \"$dir\"'"
            RC=1
        else
            cp "$readme" "$dir/TEMP_README.md"
            terraform-docs markdown table --output-file TEMP_README.md --output-mode inject "$dir" >/dev/null
            set +e
            cmp -s "$readme" "$dir/TEMP_README.md"
            set -e
            if [[ ! "$?" -eq 0 ]]; then
                echo "💣 README $readme doesn't seem to be up-to-date."
                echo "Try running 'terraform-docs markdown table --output-file README.md --output-mode inject \"$dir\"'"
                RC=1
            fi
        fi
    fi
done <<<"$MAINS"

if [[ "$RC" -eq 0 ]]; then
    echo "✨ 🍰 ✨ READMEs check passed."
else
    echo "💥 💔 💥 READMEs check failed."
    exit 1
fi
