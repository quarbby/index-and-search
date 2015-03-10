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

doc_dict = {}
all_file = set()
stop_words = set(nltk.corpus.stopwords.words('english'))
stemmer = PorterStemmer()

def index():
    for filename in os.listdir(doc_dir):
        read_file(filename)

    write_dict_and_postings_file()

def read_file(filename):
    f = open(doc_dir + "/" + filename, 'r')

    for line in f:
        words = []
        sentences = nltk.sent_tokenize(line)
        for sentence in sentences:
            word_list = nltk.word_tokenize(sentence)
            words = words + word_list

        for word in words:
            word  = process_word(word)
            add_to_dict(word, filename)

    f.close()

# dict file written as: <term> <line offset in posting file> <doc freq>
# postings file written as: (docID, term freq) (docID, term freq)...
def write_dict_and_postings_file():
    f = open(dict_file, 'w')
    f_posting = open(postings_file, 'w')

    all_file_list = ' '.join(str(file) for file in sorted(all_file))
    f_posting.write(all_file_list+'\n')
    offset = len(all_file_list+'\n')

    keylist = sorted(doc_dict.keys())

    for key in keylist:
        postings_set = OrderedDict(sorted(doc_dict[key]['list'].items(), key= lambda x: x[0]))

        f.write(key + " " + str(offset) + " " + str(len(postings_set)) + str(doc_dict[key]['df']) + "\n")    

        postings_list = [(docID, tf) for docID, tf in postings_set.items()]       # List of tuples generated from postings dictionary (docID, tf)
        
        set_string = ' '.join(str(post) for post in postings_list)
        f_posting.write(set_string + "\n")

        offset = offset + len(set_string+'\n')

    f.close()
    f_posting.close()

def process_word(word, use_stop_words=False, remove_numbers=False):
    word = filter(str.isalnum, word)    # Remove non alpha-numeric characters

    word = word.lower()

    if use_stop_words:
        if word in stop_words:
            return 

    if remove_numbers:
        num = set(string.digits)
        word = ''.join(ch for ch in word if ch not in num)

    if word == '':
        return

    word = stemmer.stem(word)
    return word

def add_to_dict(word, filename): 
    filename = filename.strip()
    word = str(word)
    all_file.add(int(filename))

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


