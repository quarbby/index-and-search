#!/bin/sh
python search.py -d dictionary.txt -p postings.txt -q q1.xml -o q1_output.txt
python search.py -d dictionary.txt -p postings.txt -q q2.xml -o q2_output.txt
python search.py -d dictionary.txt -p postings.txt -q query.xml -o output.txt
