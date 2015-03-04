#!/usr/bin/python

''' index.py for indexing the data '''

import sys
import nltk
import getopt
import os
import math 
import string

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

# dict file written as: <term> <line offset in posting file> <frequency>
# postings file just throw all the posting numbers in 
def write_dict_and_postings_file():
    f = open(dict_file, 'w')
    f_posting = open(postings_file, 'w')
    all_file_list = ' '.join(str(file) for file in sorted(all_file))
    f_posting.write(all_file_list+'\n')
    offset = len(all_file_list+'\n')
    keylist = sorted(doc_dict.keys())
    for key in keylist:
        postings_set = sorted(doc_dict[key])
        f.write(key + " " + str(offset) + " " + str(len(postings_set)) + "\n")    

        set_string = ' '.join(str(post) for post in postings_set)
        f_posting.write(set_string + "\n")

        skip_list = implement_skip_list(postings_set)
        skip_set_string = ' '.join(str(post) for post in skip_list)
        f_posting.write(skip_set_string + "\n")

        offset = offset + len(set_string+'\n'+skip_set_string+'\n')

    f.close()
    f_posting.close()

def read_file(filename):
    f = open(doc_dir + "/" + filename, 'r')

    for line in f:
        words = []
        sentences = nltk.sent_tokenize(line)
        for sentence in sentences:
            word_list = nltk.word_tokenize(sentence)
            words = words + word_list

        for word in words:
            word  = process_word(word, use_stop_words=True, remove_numbers=False)
            add_to_dict(word, filename)

    f.close()

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
    word = str(word)
    all_file.add(filename)
    if not word in doc_dict:
        doc_dict[word] = set()
        doc_dict[word].add(int(filename.strip()))
    elif not word in doc_dict.get(word):
        doc_dict[word].add(int(filename.strip()))
    else:
        pass

def implement_skip_list(posting_list):
    skip_list = []
    posting_list = list(posting_list)
    num_skips = int(math.sqrt(len(posting_list)))
    for i in range(0, len(posting_list), num_skips):
        skip_list.append(posting_list[i])

    return skip_list

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


