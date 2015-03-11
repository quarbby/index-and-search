#!/usr/bin/python

''' search.py for searching the data using LNC.LTC VSM '''

import sys
import os
import getopt
import math
import numpy as np
import shlex

import nltk
from nltk.stem.porter import PorterStemmer

dict_file = ""
postings_file = ""
query_file = ""
output_file = ""
all_file = set()

dict_words = {}

stemmer = PorterStemmer()

def process_query(query):
    ranked_result = rank_documents(query)

    return ranked_result

def rank_documents(query):
    result = []

    query_list = query.strip().split()
    query_list = map(process_word, query_list)

    scores = [0.0] * len(all_file)
    length = get_doc_length()

    for i in xrange(len(query_list)): 
        word = query_list[i]

        # Process only if word exists
        if word_in_dict(word):
            weight_tq = log_term_freq(query_list.count(word)) * inv_doc_freq(word)
            postings_list = get_postings_list(word)

            for (docID, tf) in postings_list:
                scores[docID] += calc_weight_td(docID, tf) * weight_tq

    scores = list(np.array(scores)/np.array(length))

    result = get_top_results(scores)

    return result

# Do we want to stem stop words out?
def process_word(word):
    word = word.lower()
    return stemmer.stem(word)

def get_postings_list(word):
    start = '('
    end = ')'
    posting_line = []

    with open(postings_file, 'r') as posting:
        posting.seek(int(dict_words[word][0]))
        line = posting.readline().strip()

        while len(line) > 0:
            _,_,rest = line.partition(start)
            result,_,line = rest.partition(end)

            result = result.split(',')
            q = shlex.split(result[0])[0]
            posting_line.append((int(q), int(result[1])))

    posting_line = map(lambda (x,y): (int(x), int(y)), line)

    return posting_line

def word_in_dict(word):
    if dict_words.has_key(word):
        return True
    else:
        return False

def get_top_results(scores):
    num_results = 10
    scores = np.array(scores)

    # Get the non-zero indices and original values
    non_zero = np.nonzero(scores)[0]
    original_vals = scores[non_zero]

    temp_results = sorted(enumerate(original_vals), key=lambda x: x[1])    # Sort and get indices of original list

    if len(non_zero) <= 10:
        top_results = temp_results
    else:
        top_results = temp_results[:num_results]

    return top_results

'''
Helpers for ranking
'''
# 1 + log(tf)
def log_term_freq(term_freq):
    if term_freq == 0:
        return 0
    else:
        return 1 + math.log(term_freq)

# log(N/df)
def inv_doc_freq(word):
    doc_freq = int(dict_words[word][1])
    return math.log((len(dict_words)*1.0)/ doc_freq, 10)

def normalise(vector):
    return math.sqrt(sum(x**2 for x in vector))

def get_doc_length():
    doc_length = []

    for doc in set(all_file):
        vector = []
        # We're supposed to generate a document vector
        # Not sure most efficient way to do it... we may want to use another data structure? 

        doc_length.append(vector)

    for i in xrange(len(doc_length):
        doc_length[i] = normalise(doc_length[i])        

    return doc_length

def calculate_weight_td(docID, tf):
    return log_term_freq(tf) * 1.0

# Meta data of all the files stored
def read_meta():
    global all_file
    with open(postings_file, 'r') as f:
        all_file = map(lambda x: int(x), f.readline().strip().split())

# Dict stored as term: (line offset, freq)
def read_dict():
    f = open(dict_file, 'r')
    for line in f:
        word_list = line.strip().split()
        dict_words[word_list[0]] = (word_list[1], word_list[2])
    f.close()

def search():
    read_dict()
    read_meta()

    with open(output_file, 'w') as out, open(query_file, 'r') as f:
        for query in f:
            out.write(" ".join(str(x) for x in process_query(query)) + '\n')

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
