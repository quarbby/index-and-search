#!/usr/bin/python

''' search.py for searching the data '''

import sys
import os
import getopt
import math
import nltk
from nltk.stem.porter import PorterStemmer

dict_file = ""
postings_file = ""
query_file = ""
output_file = ""
all_file = set()

dict_words = {}

stemmer = PorterStemmer()

operators = ['NOT', 'AND', 'OR']

def process_query(query):
    post_fix_query = convert_to_post_fix(query)
    result = process_post_fix(post_fix_query)

    return result

def convert_to_post_fix(query):
    op_stack = []
    output_stack = []


    # paren_query, new_query= get_parenthesis_query(query)
    # query_list = query_list + paren_query

    terms = query.strip().split()
    for term in terms:
        if (term in ['AND', 'OR', 'NOT']):
            if (term == 'AND'):
                while op_stack and op_stack[len(op_stack)-1] in ['AND', 'NOT']:       #pop if the top of op_stack is AND or NOT
                    output_stack.append(op_stack.pop())
            elif (term == 'OR'):
                while op_stack and op_stack[len(op_stack)-1] != '(':                                #since OR has lowest precedence
                    output_stack.append(op_stack.pop())
            op_stack.append(term)
        elif '(' in term:
            if term[0] == '(':
                op_stack.append('(')
                if term[1:] == 'NOT':       #this is the only operator that can be at the start of a bracket
                    op_stack.append(term[1:])
                else:
                    output_stack.append(stemmer.stem(term[1:].lower()))
            else:
                assert False, "invalid query in term \"%s\" " %(term)
        elif ')' in term:
            if term[len(term)-1] == ')':
                output_stack.append(stemmer.stem(term[:-1].lower()))
                next_op = op_stack.pop()
                while next_op != '(':
                    output_stack.append(next_op)
                    next_op = op_stack.pop()
            else:
                assert False, "invalid query in term \"%s\" " %(term)
        else:
            output_stack.append(stemmer.stem(term.lower()))
    while op_stack:
        output_stack.append(op_stack.pop())
    return output_stack

def process_post_fix(query):
    res_stack = []
    for term in query:
        if term =='AND':
            res_stack.append(process_and(res_stack.pop(), res_stack.pop()))
        elif term == 'OR':
            res_stack.append(process_or(res_stack.pop(), res_stack.pop()))
        elif term == 'NOT':
            # print result
            res_stack.append(process_not(res_stack.pop()))
        else:
            with open(postings_file, 'r') as posting:
                if term in dict_words:
                    posting.seek(int(dict_words[term][0]))
                    res_stack.append(map(lambda x: int(x), posting.readline().strip().split()))
                else :
                    res_stack.append([])
    return res_stack[0]


def process_or(posting_term1, posting_term2):
    res = []
    idx1 = 0
    idx2 = 0
    while idx1 < len(posting_term1) and idx2 < len(posting_term2):
        if (posting_term1[idx1] < posting_term2[idx2] ):
            res.append(posting_term1[idx1])
            idx1 = idx1+1
        elif (posting_term1[idx1] > posting_term2[idx2]):
            res.append(posting_term2[idx2])
            idx2 = idx2+1
        else:
            res.append(posting_term1[idx1])
            idx1 = idx1+1
            idx2 = idx2+1

    if idx2 >= len(posting_term2):
        res = res + posting_term1[idx1:]
    elif idx1 >= len(posting_term1):
        res = res + posting_term2[idx2:]
    return res

#this use implicit skip pointers instead of explicit ones
def process_and(posting_term1, posting_term2):
    res = []
    idx1 = 0
    idx2 = 0
    skip1 = int(math.sqrt(len(posting_term1)))
    skip2 = int(math.sqrt(len(posting_term2)))
    while idx1 < len(posting_term1) and idx2 < len(posting_term2):
        if posting_term1[idx1] == posting_term2[idx2]:
            res.append(posting_term1[idx1])
            idx1 = idx1+1
            idx2 = idx2+1
        else:
            if skip1 < len(posting_term1) and posting_term1[skip1] < posting_term2[idx2]:
                idx1 = skip1
                skip1 = skip1 + int(math.sqrt(len(posting_term1)))
            elif skip2 < len(posting_term2) and posting_term2[skip2] < posting_term1[idx1]:
                idx2 = skip2
                skip2 = skip2 + int(math.sqrt(len(posting_term2)))
            elif posting_term1[idx1] < posting_term2[idx2]:
                idx1 = idx1 + 1
            elif posting_term2[idx2] < posting_term1[idx1]:
                idx2 = idx2 + 1
    return res

def process_not(posting):
    res = sorted(all_file - set(posting))
    return res

def get_postings_skip_list(query_word):
    line_num = get_line_num_from_dict(query_word)

    # Query does not exist - TODO: handle return case 
    if not line_num:
        return

    # full_postings = linecache.getline(postings_file, line_num)
    # skip_list = linecache.getline(postings_file, line_num+1)
    return full_postings, skip_list

def get_line_num_from_dict(query_word):
    if not query_word in dict_words:
        return
    else:
        return dict_words[query_word][0]

# Is there a better way to store the dictionary? 
# I store it as key: word, value: (line offset, freq)
def read_dict():
    f = open(dict_file, 'r')
    for line in f:
        word_list = line.strip().split()
        dict_words[word_list[0]] = (word_list[1], word_list[2])
    f.close()

def read_meta():
    global all_file
    with open(postings_file, 'r') as f:
        all_file = set(map(lambda x: int(x), f.readline().strip().split()))

def write_result_file():
    pass

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
