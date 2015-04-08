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
dict_file = ""      # main dictionary file path (contains dictionary file paths for zones)
postings_file = ""  # main postings file path (contains postings file paths for zones)

title_dict = defaultdict(lambda: {'list': defaultdict(int), 'df': 0})       # {"<term>": {"list": {"<docId>": <tf>}, "df": <df>}}
abstract_dict = defaultdict(lambda: {'list': defaultdict(int), 'df': 0})    # {"<term>": {"list": {"<docId>": <tf>}, "df": <df>}}
IPC_dict = defaultdict(lambda: [])                                          # {"<IPC class>": [<docId>...]}
doc_IPC = {}                                                                # {"<docId>": "<IPC>"}
doc_length = {}                                                             # {"<docId>": <length of document vector>} (does not differentiate terms between title and abstract)
title_doc_length = {}                                                       # same format as doc_length but only for title zone document vectors
abstract_doc_length = {}                                                    # same format as doc_length but only for abstract zone document vectors

total_num_doc = 0   # total number of documents indexed
total_num_IPC = 0   # total number of IPC classes indexed

""" indexes each document in corpus """
def index():
    global total_num_doc
    # index every document in corpus
    for docId in os.listdir(doc_dir):
        total_num_doc += 1

        title_list, abstract_list, IPC = utils.XML_corpus_parser(doc_dir + docId)

        corpus_tf, title_tf, abstract_tf = build_corpus_dict(title_list, abstract_list, docId)
        
        # calculate vector lengths
        doc_length[docId] = get_doc_len(corpus_tf)
        title_doc_length[docId] = get_doc_len(title_tf)
        abstract_doc_length[docId] = get_doc_len(abstract_tf)

        # process IPC information
        add_to_IPC_dict(IPC, docId)
        doc_IPC[docId] = IPC

    write_files()

"""
Add each term in title and abstract to their respective zones in the dictionary.
Returns:
    corpus_tf:      maps term to term frequencies in the document, does not differetiate title and abstract terms
    title_tf:       maps term to term frequencies for terms within document title zone
    abstract_tf:    maps term to term frequencies for terms within document abstract zone
Params:
    title_list:     a list of terms in title zone for the document
    abstract_list:  a list of terms in abstract zone for the document
    docId:          document id
"""
def build_corpus_dict(title_list, abstract_list, docId):
    corpus_tf = defaultdict(int)    # {"<term>": term frequency}
    title_tf = defaultdict(int)     # {"<term>": term frequency}
    abstract_tf = defaultdict(int)  # {"<term>": term frequency}

    # Title List
    for term in title_list: 
        corpus_tf[term] += 1
        title_tf[term] += 1
        add_to_dict("title", term, docId)

    # Abstract List
    for term in abstract_list: 
        corpus_tf[term] += 1
        abstract_tf[term] += 1
        add_to_dict("abstract", term, docId)

    return corpus_tf, title_tf, abstract_tf

"""
Returns the document vector length for the given term frequencies map
Params:
    corpus_dict:    maps term to term frequencies
"""
def get_doc_len(index):
    doc_len = 0.0  # accumulator for sum of squares
    for term in index:
        w_td = (1 + math.log10(index[term]))    # component weight
        doc_len += w_td ** 2                    # accumulate sum of squares         
    return math.sqrt(doc_len)                   # return euclidean length

"""
Adds given term to its respetive zone in the dictionary
Params:
    list_type:  "title" | "abstract"
    term:       term to be added to dictionary
    docId:      document id
"""
def add_to_dict(list_type, term, docId): 
    docId = str(docId.strip())
    term = str(term)

    # determine corresponding dictionary for zone
    doc_dict = {}
    if list_type == "title":
        doc_dict = title_dict
    elif list_type == "abstract":
        doc_dict = abstract_dict

    # increase df for term if term not yet registered in term list
    if docId not in doc_dict[term]['list']:
        doc_dict[term]['df'] += 1
   
    doc_dict[term]['list'][docId] += 1 # increment tf

"""
Index IPC class
Params:
    IPC:    IPC class   
    docId:  document id
"""
def add_to_IPC_dict(IPC, docId):
    global total_num_IPC

    docId = str(docId.strip())
    IPC = str(IPC.strip())

    if IPC not in IPC_dict:
        total_num_IPC += 1      # update total number of IPC classes
    IPC_dict[IPC].append(docId) # append docId to list for IPC

"""
Writes dictionary and posting files of the following format:
main dictionary:
    <docId>:<IPC>, ...                  // first line lists out docId and their respective IPC class
    <docId>:<document length>, ...      // second line lists out document length calculated using all terms in document
    <docId>:<document length>, ...      // third line lists out document length of title zone
    <docId>:<document length>, ...      // fourth line lists out document length of abstract zone
    title:dictionary_title.txt          // title:<dictionary filename for title zone>
    abstract:dictionary_abstract.txt    // abstract:<dictionary filename for abstract zone>
    IPC:dictionary_IPC.txt              // IPC:<dictionary filename for abstract zone>

zone dictionary for title and abstract:
    <term> <byte offset in postings file> <df>
    ...
zone dictionary for IPC:
    <term> <byte offset in postings file>
    ...
main postings file:
    title:postings_title.txt            // title:<postings filename for title zone>
    abstract:postings_abstract.txt      // abstract:<postings filename for abstract zone>
    IPC:postings_IPC.txt                // IPC:<postings filename for abstract zone>

zone postings file for title and abstract:
    <docId>:<tf>, ...                   // list out docId:tf pair
    ...
zone postings file for IPC:
    <docId>, ...                        // list of docIds
    ...
"""
def write_files():
    zones = [
        {"name": "title", "dict": title_dict},
        {"name": "abstract", "dict": abstract_dict},
        {"name": "IPC", "dict": IPC_dict}
    ]
    # open main dictionary and postings files for writing
    f_dict = open(dict_file, 'w')
    f_posting = open(postings_file, 'w')
    
    # write document IPCs
    f_dict.write(','.join((docId + ':' + IPC) for docId, IPC in doc_IPC.items()) + '\n')
    # write document lengths to dictionary 
    f_dict.write(','.join((docId + ':' + str(length)) for docId, length in doc_length.items()) + '\n')
    f_dict.write(','.join((docId + ':' + str(length)) for docId, length in title_doc_length.items()) + '\n')
    f_dict.write(','.join((docId + ':' + str(length)) for docId, length in abstract_doc_length.items()) + '\n')

    # writes dictionary and postings files for each zone
    last = len(zones) - 1
    for i, zone_index in enumerate(zones):
        postings_filename, zone_dictionary = write_postings(zone_index)     # write postings
        dictionary_filename = write_dictionary(zone_index, zone_dictionary) # write dictionary
        f_posting.write(zone_index['name'] + ':' + postings_filename)       # write zone dictionary filename to main dictionary
        f_dict.write(zone_index['name'] + ':' + dictionary_filename)        # write zone postings filename to main postings file
        if i != last:
            f_posting.write('\n')
            f_dict.write('\n')
    # close files
    f_dict.close()
    f_posting.close()

"""
Writes to postings file and returns the filename written and its corresponding dictionary to be written
Params:
    zone_index:   the inverted index built for zone
"""
def write_postings(zone_index):
    dictionary = OrderedDict()              # {"<term>": {"offset": <offset>, "df": <df>}}
    offset = 0                              # byte offset in postings file
    isIPC = (zone_index['name'] == 'IPC')   # flag to indicate different handling for IPC
    postings_filename = 'postings_' + zone_index['name'] + '.txt'
    with open(postings_filename, 'w') as f:
        last = len(zone_index['dict']) - 1
        for i, pair in enumerate(zone_index['dict'].items()):
            zone_term = pair[0]
            zone_info = pair[1]
            entry = '' 
            # get entry and update dictionary
            if isIPC:
                entry = ','.join(docId for docId in zone_info)
                dictionary[zone_term] = offset
            else:
                zone_list = zone_info['list']
                df = zone_info['df']
                entry = ','.join((docId + ':' + str(zone_list[docId])) for docId in zone_list)
                dictionary[zone_term] = {'offset': offset, 'df': df}
            if i != last:
                entry += '\n'
            # write and update offset
            f.write(entry)
            offset += len(entry)     # addtional 1 character for return carriage
    return postings_filename, dictionary

"""
Writes to dictioanry file and returns the filename written
Params:
    zone_index:     the inverted index built for zone
    dictionary:     the dictionary of terms and their offsets 
"""
def write_dictionary(zone_index, dictionary):
    isIPC = (zone_index['name'] == 'IPC')   # flag to indicate different handling for IPC
    dictionary_filename = 'dictionary_' + zone_index['name'] + '.txt'
    with open(dictionary_filename, 'w') as f:
        content = ''
        if isIPC:
            content = '\n'.join((term + ' ' + str(offset)) for term, offset in dictionary.items())
        else:
            content = '\n'.join((term + ' ' + str(info['offset']) + ' ' + str(info['df'])) for term, info in dictionary.items())
        f.write(content)
    return dictionary_filename

""" Prints correct commandline usage to user """
def usage():
    print "Usage: python index.py -i dir-of-documents -d dictionary-file -p postings-file"

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')

        for opt, arg in opts:
            if opt == '-i':
                # add last slash if not there
                if (arg[-1] != '/'):
                    arg += '/'
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


""" DEPRECATED functions """
def write_dict_and_postings_file():
    """
    Dictionary format:
        <IPC> <byte offset in posting file>                 // IPC dictionary
        <term> <byte offset in posting file> <doc freq>     // title dictionary
        <term> <byte offset in posting file> <doc freq>     // abstract dictionary

    Postings File format:
        <total IPC number>    <total documents indexed> // tab separated
        <IPC> <list of docs>                            // IPC postings  
        <docId> <doc vector length>                     // doc lengths written
        (docId, term freq) (docId, term freq)...        // postings list format for title and abstract
    """
    f_dict = open(dict_file, 'w')
    f_posting = open(postings_file, 'w')

    # Writing number of docs and IPC to postings file
    total_num_str = str(total_num_IPC) + '\t' + str(total_num_doc) + '\n'
    f_posting.write(total_num_str)
    offset = len(total_num_str)

    # Writing doc lengths to postings files
    file_length_list = ' '.join((str(key) + ',' + str(doc_length[key])) for key in doc_length)
    f_posting.write(file_length_list + '\n')
    offset += len(file_length_list + '\n') 

    # Writing IPC postings into postings and dictionary files
    ipc_keys = IPC_dict.keys()
    ipc_postings = OrderedDict(sorted(IPC_dict.items()))

    for key in ipc_keys:
        f_dict.write(key + " " + str(offset) + " " + str(IPC_dict[key]) + "\n")

        ipc_postings_list = ipc_postings[key]
        ipc_postings_str = ' '.join(str(post) for post in ipc_postings_list) + "\n"
        f_posting.write(ipc_postings_str)

        offset = offset + len(ipc_postings_str)

    # Writing title dictionary postings into postings and dictionary file 
    keylist = title_dict.keys()

    for key in keylist:
        postings_set = OrderedDict(sorted(title_dict[key]['list'].items()))

        f_dict.write(key + " " + str(offset) + " " + str(title_dict[key]['df']) + "\n")

        # List of tuples generated from postings dictionary (docId, tf)
        postings_list = [str(docId) + ','+ str(tf) for docId, tf in postings_set.items()]       
        
        set_string = ' '.join(str(post) for post in postings_list) + "\n"
        f_posting.write(set_string)

        offset = offset + len(set_string)

    # Writing abstract dictionary postings into postings and dictionary file 
    keylist = abstract_dict.keys()

    for key in keylist:
        postings_set = OrderedDict(sorted(doc_dict[key]['list'].items()))

        f_dict.write(key + " " + str(offset) + " " + str(abstract_dict[key]['df']) + "\n")

        # List of tuples generated from postings dictionary (docId, tf)
        postings_list = [str(docId) + ','+ str(tf) for docId, tf in postings_set.items()]       
        
        set_string = ' '.join(str(post) for post in postings_list) + "\n"
        f_posting.write(set_string)

        offset = offset + len(set_string)

    f_dict.close()
    f_posting.close()