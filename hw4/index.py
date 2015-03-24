#!/usr/bin/python

'''
Main file used for indexing the corpus
'''

import sys
import getopt
import os
import math 
import string

from collections import OrderedDict

import utils

doc_dir = ""
dict_file = ""
postings_file = ""

doc_dict = {}
doc_length = {}
ipc_dict = {}

total_num_doc = 0
total_num_ipc = 0

def index():
	global total_num_doc

    for filename in os.listdir(doc_dir):
    	total_num_doc += 1

    	title_list, abstract_list, ipc = utils.XML_corpus_parser(filename)
    	merged_list = title_list + abstract_list

    	corpus_dict = build_corpus_dict(merged_list)
    	doc_len = get_doc_len(corpus_dict)
    	doc_length[filename] = doc_len

    	add_to_ipc_dict(ipc, filename)

    write_dict_and_postings_file()

def build_corpus_dict(merged_list):
    corpus_dict = {}
	for word in merged_list: 
		if not word in corpus_dict:
			corpus_dict[word] = 0
		corpus_dict[word] += 1
		add_to_dict(word, filename)

	return corpus_dict

def get_doc_len(corpus_dict):
	doc_len = 0.0
	for word in corpus_dict:
		doc_len += (1 + math.log10(corpus_dict[word])) ** 2
	return math.sqrt(doc_len)

def add_to_dict(word, filename): 
    filename = str(filename.strip())
    word = str(word)

    # new term
    if not doc_dict.has_key(word):
        doc_dict[word] = {'list': {}, 'df': 0}
        doc_dict[word]['df'] += 1
        doc_dict[word]['list'] = {filename: 1}
    elif word in doc_dict:
        # Term appear before, docID not. Add docID, set tf=1, increase df
        if not doc_dict[word]['list'].has_key(filename):
            doc_dict[word]['list'][filename] = 1
            doc_dict[word]['df'] += 1
        # Term appear in docID before. Increase tf
        elif doc_dict[word]['list'].has_key(filename):
            doc_dict[word]['list'][filename] += 1

def add_to_ipc_dict(ipc, filename):
	global total_num_ipc

	filename = str(filename.strip())
	ipc = str(ipc.strip())

	if not ipc_dict.has_key(ipc):
		ipc_dict[ipc] = []
		total_num_ipc += 1
	ipc_dict[ipc].append(filename)

'''
dict file 
IPC dictionary written as: <ipc> <byte offset in posting file>
dictionary written as: <term> <byte offset in posting file> <doc freq>

postings file
first line write total number IPC and total number of docs
IPC postings written as: <IPC> <list of docs> 
doc lengths written as: <doc> <doc_length>
doc postings written as: (docID, term freq) (docID, term freq)...

'''
def write_dict_and_postings_file():
    f_dict = open(dict_file, 'w')
    f_posting = open(postings_file, 'w')

    # Writing number of docs and IPC to postings file 
    total_num_str = str(total_num_ipc) + '\t' + str(total_num_doc) + '\n'
    f_posting.write(total_num_str)
    offset = len(total_num_str)

    # Writing doc lengths to postings files
    file_length_list = ' '.join((str(key) + ',' +  str(doc_length[key])) for key in doc_length)
    f_posting.write(file_length_list+'\n')
    offset += len(file_length_list+'\n') 

    # Writing IPC postings into postings and dictionary files
    ipc_keys = ipc_dict.keys()
    ipc_postings = OrderedDict(sorted(ipc_dict[key].items(), key = lambda x: x[0]))

    for key in ipc_keys:
    	f_dict.write(key + " " + str(offset) + " " + str(ipc_dict[key]) + "\n")

    	ipc_postings_list = ipc_postings[key]
    	ipc_postings_str = ' '.join(str(post) for post in postings_list) + "\n"
    	f_posting.write(ipc_postings_str)

    	offset = offset + len(ipc_postings_str)

    # Writing doc postings into postings and dictionary file 
    keylist = doc_dict.keys()

    for key in keylist:
        postings_set = OrderedDict(sorted(doc_dict[key]['list'].items(), key= lambda x: x[0]))

        f_dict.write(key + " " + str(offset) + " " + str(doc_dict[key]['df']) + "\n")

		# List of tuples generated from postings dictionary (docID, tf)
        postings_list = [str(docID) + ','+ str(tf) for docID, tf in postings_set.items()]       
        
        set_string = ' '.join(str(post) for post in postings_list) + "\n"
        f_posting.write(set_string)

        offset = offset + len(set_string)

    f_dict.close()
    f_posting.close()

def usage():
    print "Usage: python index.py -i dir-of-documents -d dictionary-file -p postings-file"

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')

        for opt, arg in opts:
            if opt == '-i':
                doc_dir = arg
            elif opt == '-d':
                dict_file = arg
            elif opt == '-p':
                postings_file = arg
            else:
                assert False, "unhandled option"

    except getopt.GetoptError:
        usage()
        sys.exit(2)

    if doc_dir == "" or dict_file == "" or postings_file == "":
        usage()
        sys.exit(2)

    index()