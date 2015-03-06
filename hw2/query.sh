#!/bin/sh
python search.py -d dictionary.txt -p postings.txt -q queries_forum.txt -o output_forum.txt
python search.py -d dictionary.txt -p postings.txt -q query.txt -o output.txt