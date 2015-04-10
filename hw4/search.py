#!/usr/bin/python

""" For searching the data using LNC.LTC VSM """ 
from collections import defaultdict
import getopt
import heapq
import utils
import math
import sys
import os
import io

dict_file = ""          # main dictionary file path (contains dictionary file paths for zones)
postings_file = ""      # main postings file path (contains postings file paths for zones)
zones = {
    'title': {
        'dict': {},     # {"<term>": {"offset": <byte offset>, "df": <df>}}
        'post': None,   # opened postings file for title
        'length': {}    # {"<docId>": <length of document vector in title zone>}
    },            
    'abstract': {
        'dict': {},     # {"<term>": {"offset": <byte offset>, "df": <df>}}
        'post': None,   # opened postings file for abstract
        'length': {}    # {"<docId>": <length of document vector in abstract zone>}
    },
    'IPC': {
        'dict': {},     # {"<term>": <offset>}
        'post': None    # opened postings file for IPC
    },
    'family_members': {
        'dict': {},     # {"<term>": <offset>}
        'post': None    # opened postings file for family_member
    },
}
query_file = ""         # file for queries
output_file = ""        # file for retrieved results

doc_IPC = {}            # {"<docId>": "<IPC>"}
doc_length = {}         # {"<docId>": <length of document vector>} does not between title and abstract

total_num_doc = 0   # total number of documents indexed
total_num_IPC = 0   # total number of IPC classes indexed

def search():
    # read in metadata and process zone dictionaries and postings files
    process_main_dict(dict_file)
    process_main_post(postings_file)

    # get title and descritpion terms from query
    query_title, query_desc = utils.XML_query_parser(query_file)

    # Expand query title and description using google
    expanded_title, expanded_desc = utils.query_expansion_google(query_title)
    query_title += expanded_title
    query_desc += expanded_desc

    # Expand query title and decription using wordnet
    query_title += utils.query_expansion_wordnet(query_title)
    query_desc += utils.query_expansion_wordnet(query_desc)
    
    # get query terms
    query_title_terms = utils.get_terms_list(' '.join(word for word in query_title))
    query_desc_terms = utils.get_terms_list(' '.join(word for word in query_desc))

    # get document scores and retrieve documents
    scores = get_document_scores(query_title_terms, query_desc_terms)
    output = filter_documents_with_threshold(scores)
    
    # write output
    write_output_file(output)

    # close postings files
    for zone_name in zones:
        zones[zone_name]['post'].close()

"""
Returns all retreived documents with their respective scores
Params:
    query_title_terms:  list of terms in query title
    query_desc_terms:   list of terms in query description
"""
def get_document_scores(query_title_terms, query_desc_terms):
    query_title_tf = get_tf_dict(query_title_terms) # term to tf map for query title terms
    query_desc_tf = get_tf_dict(query_desc_terms)   # term to tf map for query description terms
    # tabulate scores
    total_scores = defaultdict(float)                                   # accumulator for scores
    update_cosine_scores(total_scores, query_title_tf, "title", 4.0)    # score using query title against title zone
    update_cosine_scores(total_scores, query_desc_tf, "title", 1.0)     # score using query description against title zone
    update_cosine_scores(total_scores, query_title_tf, "abstract", 4.0) # score using query title against abstract zone
    update_cosine_scores(total_scores, query_desc_tf, "abstract", 1.0)  # score using query description against abstract zone
    return total_scores

"""
Given a list of terms, returns a dictionary that maps terms to weighted term frequencies
Params:
    terms: list of terms
"""
def get_tf_dict(terms):
    tf_dict = defaultdict(float)
    # tabulate raw term frequencies
    for term in terms:
        tf_dict[term] += 1
    # update dictionary with weighted term frequencies
    for term in tf_dict:
        tf_dict[term] = 1 + math.log(tf_dict[term], 10)
    return tf_dict

"""
Performs filtering on the list of documents based on scores derived and return documents that remains 
Params:
    scores: {"<docId>": <score>}
"""
def filter_documents_with_threshold(scores):
    # TODO perform filtering based on IPC
    # return [str(i[0]) + "," + str(i[1]) for i in sorted(scores.items(), key = lambda x:x[1], reverse = True)]
    sorted_results = [i for i in sorted(scores.items(), key = lambda x:x[1], reverse = True)]
    top_IPCs = map(lambda x: doc_IPC[x[0]], sorted_results[:10])
    # top_IPC = max(set(top_10_IPC), key=top_10_IPC.count)
    top_scores = sorted_results[0][1]
    sorted_results = filter(lambda x: doc_IPC[x[0]] in top_IPCs and x[1]/top_scores >= 0.1, sorted_results)
    return map(lambda x: x[0], sorted_results)


"""
Performs filtering on the list of documents based on scores derived and return documents that remains 
Params:
    scores: {"<docId>": <score>}
"""
def filter_documents(scores):
    # TODO perform filtering based on IPC
    # return [str(i[0]) + "," + str(i[1]) for i in sorted(scores.items(), key = lambda x:x[1], reverse = True)]
    sorted_results = [i[0] for i in sorted(scores.items(), key = lambda x:x[1], reverse = True)]
    top_IPCs = map(lambda x: doc_IPC[x], sorted_results[:10])
    # top_IPC = max(set(top_10_IPC), key=top_10_IPC.count)
    return filter(lambda x: doc_IPC[x] in top_IPCs, sorted_results)



"""
Params:
    total_scores:   total scores to be updated with current query
    querty_tf:      query term to term frequency map
    zone_name:      'title' | 'abstract'
    conf_wt:        confidence weigght
"""
def update_cosine_scores(total_scores, query_tf, zone_name, conf_wt):
    scores = defaultdict(float)                     # (accumulator) Key: docId, Value: raw tabulated score (before cosine normalization)
    zone_dict = zones[zone_name]['dict']            # dictionary for zone
    zone_postings_file = zones[zone_name]['post']   # postings file for zone
    vector_lengths = zones[zone_name]['length']     # vector lengths for zone
    N = len(vector_lengths)                         # number of documents in zone

    # for each query term
    for term, tf in query_tf.items():
        if (term not in zone_dict):    continue    # skip terms not in dictionary
        df = zone_dict[term]['df']
        idf = math.log(N/float(df), 10)
        w_tq = tf * idf    # weight for term in query

        # for each document in postings list
        for docId, tf_raw_document in load_posting_list(zone_postings_file, zone_dict[term]['offset']):
            w_td = 1 + math.log(tf_raw_document, 10)    # weight for term in current document
            scores[docId] += (w_tq * w_td) * conf_wt    # accumulate scores

    # update total_scores with length normalized scores
    for docId in scores:
        total_scores[docId] += scores[docId]/vector_lengths[docId]

"""
Returns a list of docID,tf pairs for the respective postings list
Params:
    posting_file:   the postings file to retrieve postings list from
    offest:         byte offset in postings file
"""
def load_posting_list(posting_file, offset):
    posting_file.seek(offset)
    line = posting_file.readline()
    # construct list of pairs
    posting_list = []
    for token in line.split(','):
        pair = token.split(':')
        posting_list.append((pair[0], int(pair[1])))
    return posting_list


""" I/O functions """

"""
Process main dictionary by loading all zone dictionaries
Params:
    filename: filename for main dictionary
"""
def process_main_dict(filename):
	# get lines from main dictionary
    lines = []
    with open(filename) as f:
        lines = f.read().split('\n')
    
    # load metainformation
    load_meta(doc_IPC, lines[0], False)                     # load doc_IPC
    load_meta(doc_length, lines[1], True)                   # load doc_length
    load_meta(zones['title']['length'], lines[2], True)     # load title_doc_length
    load_meta(zones['abstract']['length'], lines[3], True)  # load abstract_doc_length
    
    # load dictionaries for each zone
    for line in lines[4:7]:
        token = line.split(':')
        zone_name = token[0]
        filename = token[1]
        load_dict(zone_name, filename)

    global total_num_doc, total_num_IPC
    total_num_doc = len(doc_length)             # evaulate total number of documents indexed
    total_num_IPC = len(zones['IPC']['dict'])   # evaluate total number of IPC classes indexed

"""
Process main postings file and load all filenames of zone postings files
Params:
    filename: filename for main postings file
"""
def process_main_post(filename):
    with open(filename, 'r') as f:
        for line in f.read().split('\n'):
            token = line.split(':')
            zone_name = token[0]
            post_filename = token[1]
            zones[zone_name]['post'] = io.open(post_filename, 'rb')

"""
Load metainformation for document lengths to memory
Params:
    meta_dict:      doc_IPC | doc_length | title_doc_length | abstract_doc_length
    is_value_float: to differentiate length floats and IPC strings for value
"""
def load_meta(meta_dict, line, is_value_float):
    for token in line.split(','):
        pair = token.split(':')
        docId = pair[0]
        value = pair[1]
        if is_value_float:
            value = float(value)
        meta_dict[docId] = value

"""
Load into memory the zone dictionary for the given zone
Params:
    zone_name:  'title' | 'abstract' | 'IPC'
    filename:   filename for zone dictionary
"""
def load_dict(zone_name, filename):
    zone_dict = zones[zone_name]['dict']
    with open(filename, 'r') as f:
        for line in f.read().split('\n'):
            tokens = line.split(' ')
            term = tokens[0]
            offset = int(tokens[1])
            # if IPC zone
            if zone_name == 'IPC':
                zone_dict[term] = offset
            # else if title or abstract zone
            else:
                df = tokens[2]
                zone_dict[term] = {'offset': offset, 'df': df}

"""
Writes retrieved documents in output file
Params:
    output: list of docIds retrieved
"""
def write_output_file(output):
	with open(output_file, 'w') as out:
		out.write(" ".join(str(doc) for doc in output) + '\n')

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


""" Deprecated functions"""

def get_zone_weight(zone_type):
    zone_weights = {'title': 0.30, 'desc': 0.40, 'ipc': 0.30}
    return zone_weights[zone_type.lower()]

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