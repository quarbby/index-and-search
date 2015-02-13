#!/usr/bin/python

''' search.py for searching the data '''

import sys
import os
import getops

import nltk
import linecache

dict_file = ""
postings_file = ""
query_file = ""
output_file = ""

operators = ['(', ')', 'NOT', 'AND', 'OR']

def process_query(query):
    query_list = []

    paren_query, new_query= get_parenthesis_query(query)
    query_list = query_list + paren_query

# Get query within parenthesis
def get_parenthesis_query(query):
    paren_query = []
    while operators[0] and operators[1] in query:
        op_open_bracket = query.find(operators[0])
        op_close_bracket = query.find(operators[1])
        sub_query = query[op_open_bracket+1:op_close_bracket] 
        paren_query.append(query)
        query = query[:op_open_bracket] + query[op_close_bracket+1:]

    # Process each sub query for AND OR NOT operators
    for sub_query in paren_query:
        sub_query = process_not(sub_query)

    return paren_query, query

def process_not(query):
    pass

def get_postings_skip_list(line_num):
    full_postings = linecache.getline(postings_file, line_num)
    skip_list = linecache.getline(postings_file, line_num+1)
    return full_postings, skip_list

def search():
    f = open(query_file, 'r')
    for query in f:
        process_query(query)
    f.close()

def usage():
    print "Usage python search.py -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results"

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')

        for opt, arg in opts:
            if opt == '-d':
                dict_file = arg
            elif opt == '-p':
                postings_file = arg
            elif opt == '-q':
                print "Query", arg
                query_file = arg
            elif opt == '-o':
                print "Output", arg
                output_file = arg
            else:
                assert False, "unhandled option"

    except getopt.GetoptError:
        usage()
        sys.exit(2)

    if dict_file == "" or postings_file == "" or \
            query_file == "" or output_file == "":
                print "Here"
                usage()
                sys.exit(2)

    search()
