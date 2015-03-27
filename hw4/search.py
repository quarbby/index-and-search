#!/usr/bin/python

''' 
For searching the data using LNC.LTC VSM 
'''

import sys
import os
import getopt
import math
import heapq

import utils

dict_file = ""
postings_file = ""
query_file = ""
output_file = ""

doc_len = {}
ipc_dict = {}
words_dict = {}
total_num_docs = 0
total_num_ipc = 0

def search():
    read_meta()
    read_dict()

    query_title_list, query_desc_list = utils.XML_query_parser(query_file)
    # If you want to use query from google
    queried_result_from_google = utils.query_expansion(query_title_list)
    # If you want to use wordnet query
    queried_result_from_wordnet = utils.query_expansion_wordnet(query_title_list)

    write_output_file(output)

def get_zone_weight(zone_type):
    zone_weights = {'title': 0.30, 'desc': 0.40, 'ipc': 0.30}
    return zone_weights[zone_type.lower()]


'''
I/O Helpers
'''

def read_meta():
	pass

def read_dict():
	pass

def write_output_file(output):
	with open(output_file, 'w') as out:
		out.write(" ".join(str(doct)) for doc in output+ '\n')

'''
Helpers for ranking
'''

def calc_weight_td(docID, tf):
    return log_term_freq(tf) * 1.0

# 1 + log(tf)
def log_term_freq(term_freq):
    if term_freq == 0:
        return 0
    else:
        return 1 + math.log10(term_freq)

# log(N/df)
def inv_doc_freq(word):
    doc_freq = float(dict_words[word][1])
    return math.log10((total_num_doc*1.0)/ doc_freq)

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
                query_file = arg
            elif opt == '-o':
                output_file = arg
            else:
                assert False, "unhandled option"

    except getopt.GetoptError:
        usage()
        sys.exit(2)

    if "" in [dict_file, postings_file, query_file, output_file]:
        usage()
        sys.exit(2)

    search()
