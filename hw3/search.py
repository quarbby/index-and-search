#!/usr/bin/python

''' search.py for searching the data using LNC.LTC VSM '''

import sys
import os
import getopt
import math
import shlex

import nltk
from nltk.stem.porter import PorterStemmer
import heapq

dict_file = ""
postings_file = ""
query_file = ""
output_file = ""
doc_len = {}

total_num_doc = 0

dict_words = {}

stop_words = set(nltk.corpus.stopwords.words('english'))
stemmer = PorterStemmer()

def process_query(query):
    ranked_result = rank_documents(query)
    return ranked_result

def rank_documents(query):
    result = []
    num_results = 10

    query_list = query.strip().split()
    query_list = map(process_word, query_list)

    scores = {}

    for word in query_list: 

        # Process only if word exists
        if word_in_dict(word):
            weight_tq = log_term_freq(query_list.count(word)) * inv_doc_freq(word)
            postings_list = get_postings_list(word)

            for docID, tf in postings_list:
                if docID not in scores:
                    scores[docID] = calc_weight_td(docID, tf) * weight_tq
                else:
                    scores[docID] += calc_weight_td(docID, tf) * weight_tq

    res = []
    for doc in scores:
        if scores[doc] > 0:
            if (len(res) < num_results):        #if the heap is not full, continue adding
                res.append((float(scores[doc])/float(doc_len[doc]),int(doc)))
            else:                               #if it's full, then push and pop to maintain the size of the heap
                heapq.heappushpop(res, (float(scores[doc])/float(doc_len[doc]),int(doc)))

    return sorted(res, reverse=True)

# Do we want to stem stop words out?
def process_word(word):
    word = word.lower()
    if word in stop_words:
        return
    return stemmer.stem(word)

def get_postings_list(word):
    posting_line = []

    with open(postings_file, 'r') as posting:
        posting.seek(int(dict_words[word][0]))      #retrieve the term's posting
        line = posting.readline()
        line = line.strip().split()
        for doc in line:
            temp = doc.split(',')
            posting_line.append((int(temp[0]), int(temp[1])))

    return posting_line

def word_in_dict(word):
    if dict_words.has_key(word):
        return True
    else:
        return False

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

def normalise(vector):
    return math.sqrt(sum(x**2 for x in vector))


# Meta data of all the files stored
def read_meta():
    global doc_len
    global total_num_doc
    with open(postings_file, 'r') as f:
        total_num_doc = int(f.readline().strip())
        doc_len_line = f.readline().split()
        for doc in doc_len_line:
            temp = doc.split(',')
            try:
                doc_len[int(temp[0])] = float(temp[1])
            except: 
                pass

# Dict stored as term: (line offset, freq)
def read_dict():
    f = open(dict_file, 'r')
    for line in f:
        word_list = line.strip().split()
        dict_words[word_list[0]] = (int(word_list[1]), int(word_list[2])) #both df and offset are number
    f.close()

def search():
    read_dict()
    read_meta()

    with open(output_file, 'w') as out, open(query_file, 'r') as f:
        for query in f:
            out.write(" ".join(str(x[1]) for x in process_query(query)) + '\n')

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
