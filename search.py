#!/usr/bin/python

''' search.py for searching the data '''

import sys
import os
import getopt

import nltk
import linecache

dict_file = ""
postings_file = ""
query_file = ""
output_file = ""
all_file = set()

dict_words = {}

operators = ['(', ')', 'NOT', 'AND', 'OR']

def process_query(query):

    post_fix_query = convert_to_post_fix(query)
    result = process_post_fix(post_fix_query)

    return

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
                output_stack.append(term[1:])
                op_stack.append('(')
            else:
                assert False, "invalid query in term \"%s\" " %(term)
        elif ')' in term:
            if term[len(term)-1] == ')':
                output_stack.append(term[:-1])
                next_op = op_stack.pop()
                while next_op != '(':
                    output_stack.append(next_op)
                    next_op = op_stack.pop()
            else:
                assert False, "invalid query in term \"%s\" " %(term)
        else:
            output_stack.append(term)
    while op_stack:
        output_stack.append(op_stack.pop())
    return output_stack

def process_post_fix(query):
    stack = []
    for term in query:
        if term in ['AND', 'OR']:
            pass
        elif term == 'NOT':
            pass
        else:
            stack.append(term)

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

def process_or(query1, query2):
    query1_list, _ = get_postings_skip_list(query1)
    query2_list, _ = get_postings_skip_list(query2)
    return query1_list + query2_list

#TODO: This is not using skip lists yet :( 
def process_and(query1, query2):
    query1_list, _ = get_postings_skip_list(query1)
    query2_list, _ = get_postings_skip_list(query2)
    return filter(lambda x:x in query1_list, query2_list)

def process_not(query):
    pass

def get_postings_skip_list(query_word):
    line_num = get_line_num_from_dict(query_word)

    # Query does not exist - TODO: handle return case 
    if not line_num:
        return

    full_postings = linecache.getline(postings_file, line_num)
    skip_list = linecache.getline(postings_file, line_num+1)
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
    with open(postings_file, 'r') as f:
        all_file = set(f.readline().strip().split())
    print all_file

def write_result_file():
    pass

def search():
    read_dict()
    read_meta()
    f = open(query_file, 'r')
    for query in f:
        process_query(query)

    write_result_file()
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

    if "" in [dict_file, postings_file, query_file, output_file]:
        usage()
        sys.exit(2)

    search()
