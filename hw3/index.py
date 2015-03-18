#!/usr/bin/python

''' index.py for indexing the data with VSM '''

import sys
import nltk
import getopt
import os
import math 
import string

from collections import OrderedDict

from nltk.stem.porter import PorterStemmer

doc_dir = ""
dict_file = ""
postings_file = ""
total_num_doc = 0

doc_dict = {}
doc_length = {}
stop_words = set(nltk.corpus.stopwords.words('english'))
stemmer = PorterStemmer()

def index():
    for filename in os.listdir(doc_dir):
        doc_length[filename] = read_file(filename)

    write_dict_and_postings_file()

def read_file(filename):
    global total_num_doc
    with open(doc_dir+"/"+filename,'r') as f:
        total_num_doc+=1
        dictionary = {}
        doc_len = 0.0
        for line in f:
            words = nltk.word_tokenize(line)
            
            for word in words:
                word  = process_word(word, remove_stop_words=True, remove_numbers=True)
                if word:
                    if word not in dictionary:
                        dictionary[word] = 0
                    dictionary[word] += 1
                    add_to_dict(word, filename)
        for word in dictionary:
            doc_len += (1 + math.log10(dictionary[word]))**2
        doc_len = math.sqrt(doc_len)
    return doc_len

def process_word(word, remove_stop_words=False, remove_numbers=False):

    word = word.lower()

    if remove_stop_words and word in stop_words:
            return 

    if remove_numbers and word.isdigit():
            return

    word = stemmer.stem(word)

    if (len(word) < 3):
        return
    return word

def add_to_dict(word, filename): 
    filename = int(filename.strip())
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


# dict file written as: <term> <byte offset in posting file> <doc freq>
# postings file written as: (docID, term freq) (docID, term freq)...
def write_dict_and_postings_file():
    f = open(dict_file, 'w')
    f_posting = open(postings_file, 'w')

    f_posting.write(str(total_num_doc)+'\n')
    offset = len(str(total_num_doc) + '\n')

    file_length_list = ' '.join((str(key) + ',' +  str(doc_length[key])) for key in doc_length)
    f_posting.write(file_length_list+'\n')
    offset += len(file_length_list+'\n') 

    keylist = doc_dict.keys()

    for key in keylist:
        postings_set = OrderedDict(sorted(doc_dict[key]['list'].items(), key= lambda x: x[0]))

        f.write(key + " " + str(offset) + " " + str(doc_dict[key]['df']) + "\n")

        postings_list = [str(docID) + ','+ str(tf) for docID, tf in postings_set.items()]       # List of tuples generated from postings dictionary (docID, tf)
        
        set_string = ' '.join(str(post) for post in postings_list) + "\n"
        f_posting.write(set_string)

        offset = offset + len(set_string)

    f.close()
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


