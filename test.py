#!/usr/bin/python

'''
Testing files
'''

import nltk
import sys
import linecache

dict_file = "dictionary.txt"
postings_file = "postings.txt"

def test_seek(word):
    word = word.lower()
    f_dict = open(dict_file, 'r')
    word_poz = f_dict.read().find(word)
    print word_poz
    f_dict.seek(word_poz)
    print f_dict.readline()

def test_get_line(word):
    word = word.lower()
    num_lines = 1
    f = open(dict_file, 'r')
    for line in f:
        num_lines += 1
        if (line.find(word) >= 0):
            print num_lines
            print linecache.getline(dict_file, num_lines)

def get_postings_list(line_num):
    f_postings = open(postings_file, 'r')
    line = linecache.getline(postings_file, line_num)
    print line
    
