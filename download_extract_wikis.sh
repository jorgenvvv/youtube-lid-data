#!/bin/bash

# === INFO ===
# A script to download Wikipedia dumps, extract them and concatenate into one long file.
# 
# This script needs WikiExtractor.py (in the same directory) to extract the downloaded wikipedia dumps.
# It be downloaded from: 
#  - https://raw.githubusercontent.com/attardi/wikiextractor/master/WikiExtractor.py 
#
# Flags:
#   [-d] download only, only downloads the dumps
#   [-e] extract only, only extracts the dumps
# ============

# === CONFIG ===
# URL to dumps site, can be the main Wikipedia dumps repository or a mirror
# All options are visible here https://dumps.wikimedia.org/
dumps_url=https://ftp.acc.umu.se/mirror/wikimedia.org/dumps/

# Array of language codes to download and process
# (Wiki language code from here: https://meta.wikimedia.org/wiki/List_of_Wikipedias)
download_wikis=("et")

# Output path where to download and extract the wikipedia dumps
output_path="./"

# Wikipedia dump date
# Make sure dumps for this date actually exist
wiki_date="20200101"
# ==============

extract_only=false
download_only=false
while getopts :e:d opt; do
    case $opt in 
        e) extract_only=true ;;
        d) download_only=true ;;
       \?) echo "Unknown option -$OPTARG"; exit 1;;
    esac
done

if ! $extract_only; then
    printf -- "Starting wiki dump collection process \n"

    for i in "${download_wikis[@]}"
    do
        printf -- "Downloading ${i}wiki \n"
        URL="${dumps_url}${i}wiki/${wiki_date}/${i}wiki-${wiki_date}-pages-articles.xml.bz2"
        wget $URL -P $output_path/raw_dumps -q --show-progress
    done

    echo -e "\e[32mSUCCESS: All dumps downloaded\e[0m"
fi

if ! $download_only; then
    printf -- "Starting to extract wikidumps \n"

    if ! test -f "./WikiExtractor.py"; then
        echo -e "\e[31mERROR: Cannot extract dumps, there is no Wikiextractor.py in current directory!\e[0m"
        exit 1
    fi

    for i in "${download_wikis[@]}"
    do
        printf -- "Extracting ${i}wiki \n"
        FILE="${output_path}/raw_dumps/${i}wiki-${wiki_date}-pages-articles.xml.bz2"
        ./WikiExtractor.py -o $output_path/raw_dumps/extracted $FILE --no_templates --quiet --processes 8 --min_text_length 1000 --json
        OUTPUTFILE="${i}_wiki.extracted.txt"
        mkdir -p $output_path/extracted_dumps_json
        find $output_path/raw_dumps/extracted/ -type f -name '*' -exec cat {} \; > $output_path/extracted_dumps_json/$OUTPUTFILE
        rm -rf $output_path/raw_dumps/extracted
    done

    echo -e "\e[32mSUCCESS: All dumps extracted\e[0m"
fi

