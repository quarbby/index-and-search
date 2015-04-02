#!/usr/bin/python

""" This program is the indexer for the corpus """
from collections import OrderedDict
from collections import defaultdict
import string
import getopt
import utils
import math 
import sys
import os

doc_dir = ""        # corpus directory path
dict_file = ""      # dictionary file path
postings_file = ""  # postings file path

title_dict = defaultdict(lambda: {'list': defaultdict(int), 'df': 0})       # {"<term>": {"list": {"<filename>": <tf>}, "df": <df>}}
abstract_dict = defaultdict(lambda: {'list': defaultdict(int), 'df': 0})    # {"<term>": {"list": {"<filename>": <tf>}, "df": <df>}}
doc_length = {}                                                             # {"<filename>": <length of document vector>}
ipc_dict = defaultdict(lambda: [])                                          # {"<IPC class>": [<filename>...]}

total_num_doc = 0   # total number of documents indexed
total_num_IPC = 0   # total number of IPC classes indexed

""" indexes each document in corpus """
def index():
    global total_num_doc

    for filename in os.listdir(doc_dir):
        total_num_doc += 1

        title_list, abstract_list, IPC = utils.XML_corpus_parser(doc_dir + filename)

        corpus_dict = build_corpus_dict(title_list, abstract_list, filename) # {"<term>": term frequency}
        doc_len = get_doc_len(corpus_dict) # document vector length
        doc_length[filename] = doc_len     # update doc_length dict

        add_to_ipc_dict(IPC, filename)

    write_dict_and_postings_file()

"""
Add each term in title and abstract to theuir respective zones in the dictionary.
Returns a corpus_dict which maps term to term frequencies in the document
Params:
    title_list:     a list of terms in title zone for the document
    abstract_list:  a list of terms in abstract zone for the document
    filename:       document id
"""
def build_corpus_dict(title_list, abstract_list, filename):
    corpus_dict = defaultdict(int)    # {"<term>": term frequency}

    # Title List
    for term in title_list: 
        corpus_dict[term] += 1
        add_to_dict("title", term, filename)

    # Abstract List
    for term in abstract_list: 
        corpus_dict[term] += 1
        add_to_dict("abstract", term, filename)

    return corpus_dict

"""
Returns the document vector length for the given term frequencies map
Params:
    corpus_dict:    maps term to term frequencies
"""
def get_doc_len(corpus_dict):
    doc_len = 0.0  # accumulator for sum of squares
    for term in corpus_dict:
        w_td = (1 + math.log10(corpus_dict[term]))    # component weight
        doc_len += w_td ** 2                          # accumulate sum of squares         
    return math.sqrt(doc_len) # return euclidean length

"""
Adds given term to its respetive zone in the dictionary
Params:
    list_type:  "title" | "abstract"
    term:       term to be added to dictionary
    filename:   document id
"""
def add_to_dict(list_type, term, filename): 
    filename = str(filename.strip())
    term = str(term)

    # determine corresponding dictionary for zone
    doc_dict = {}
    if list_type == "title":
        doc_dict = title_dict
    elif list_type == "abstract":
        doc_dict = abstract_dict

    # increase df for term if term not yet registered in term list
    if filename not in doc_dict[term]['list']:
        doc_dict[term]['df'] += 1
   
    doc_dict[term]['list'][filename] += 1 # increment tf

"""
Index IPC class
Params:
    IPC:        IPC class   
    filename:   document id
"""
def add_to_ipc_dict(IPC, filename):
    global total_num_IPC

    filename = str(filename.strip())
    IPC = str(IPC.strip())

    if IPC not in ipc_dict:
        total_num_IPC += 1            # update total number of IPC classes
    ipc_dict[IPC].append(filename)    # append filename to list for IPC

'''
dict file 
IPC dictionary written as: <ipc> <byte offset in posting file>
title dictionary written as: <term> <byte offset in posting file> <doc freq>
abstract dictionary written as: <term> <byte offset in posting file> <doc freq>

postings file
first line write total number IPC and total number of docs
IPC postings written as: <IPC> <list of docs> 
doc lengths written as: <doc> <doc_length>
title postings written as: (docID, term freq) (docID, term freq)...
abstract postings written as: (docID, term freq) (docID, term freq)...

'''
def write_dict_and_postings_file():
    f_dict = open(dict_file, 'w')
    f_posting = open(postings_file, 'w')

    # Writing number of docs and IPC to postings file 
    total_num_str = str(total_num_IPC) + '\t' + str(total_num_doc) + '\n'
    f_posting.write(total_num_str)
    offset = len(total_num_str)

    # Writing doc lengths to postings files
    file_length_list = ' '.join((str(key) + ',' +  str(doc_length[key])) for key in doc_length)
    f_posting.write(file_length_list+'\n')
    offset += len(file_length_list+'\n') 

    # Writing IPC postings into postings and dictionary files
    ipc_keys = ipc_dict.keys()
    ipc_postings = OrderedDict(sorted(ipc_dict.items()))

    for key in ipc_keys:
        f_dict.write(key + " " + str(offset) + " " + str(ipc_dict[key]) + "\n")

        ipc_postings_list = ipc_postings[key]
        ipc_postings_str = ' '.join(str(post) for post in ipc_postings_list) + "\n"
        f_posting.write(ipc_postings_str)

        offset = offset + len(ipc_postings_str)

    # Writing title dictionary postings into postings and dictionary file 
    keylist = title_dict.keys()

    for key in keylist:
        postings_set = OrderedDict(sorted(title_dict[key]['list'].items()))

        f_dict.write(key + " " + str(offset) + " " + str(title_dict[key]['df']) + "\n")

        # List of tuples generated from postings dictionary (docID, tf)
        postings_list = [str(docID) + ','+ str(tf) for docID, tf in postings_set.items()]       
        
        set_string = ' '.join(str(post) for post in postings_list) + "\n"
        f_posting.write(set_string)

        offset = offset + len(set_string)

    # Writing abstract dictionary postings into postings and dictionary file 
    keylist = abstract_dict.keys()

    for key in keylist:
        postings_set = OrderedDict(sorted(doc_dict[key]['list'].items()))

        f_dict.write(key + " " + str(offset) + " " + str(abstract_dict[key]['df']) + "\n")

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

    index() # run index