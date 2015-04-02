#!/usr/bin/python

""" General utility functions such as language parsing and XML parsing """
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
from nltk.corpus import wordnet
from xml.dom import minidom
import urllib2
import pprint
import json
import nltk

stop_words = set(nltk.corpus.stopwords.words('english'))    # stopwords set
stemmer = PorterStemmer()                                   # stemming instance
lemmatizer = WordNetLemmatizer()                            # lemmatizing instance

"""
Returns processed word after casefolding, stopword filtering, lemmatization and stemming
Params:
    word:               word to process 
    remove_stop_words:  if removing stopwords
    remove_numbers:     if removing numbers
"""
def process_word(word, remove_stop_words=False, remove_numbers=False):
    term = filter(str.isalnum, word)    # Remove non alpha-numeric character
    term = term.lower()                 # casefolding

    if (remove_stop_words and term in stop_words) or (remove_numbers and term.isdigit()):
        return None
    term = lemmatizer.lemmatize(term)   # lematization
    term = stemmer.stem(term)           # stemming

    return term if (len(term) > 2) else None

"""
Returns two Lists of processed terms, one from the title and one from the description of the query
Params:
    filename: document ID
"""
def XML_query_parser(filename):
    dom = minidom.parse(filename)
    title = dom.getElementsByTagName('title')[0].firstChild.nodeValue.strip().encode('utf-8')
    description = dom.getElementsByTagName('description')[0].firstChild.nodeValue.strip().encode('utf-8')
    description = description[32:] # Remove the words 'Relevant documents will describe' from the description
    return get_terms_list(title), get_terms_list(description)

"""
Returns list of processed words from title, abstract and the IPC number
Params:
    filename: document ID
"""
def XML_corpus_parser(filename):
    title = ""
    abstract = ""
    IPC = ""

    dom = minidom.parse(filename)
    for node in dom.getElementsByTagName('str'):
        if node.firstChild:
            tag = node.attributes.item(0).value.strip()
            value = node.firstChild.nodeValue.strip().encode('utf-8')

            if tag == 'Title': 
                title = value
            elif tag == 'Abstract':
                abstract = value
            elif tag == "IPC Class":
                IPC = value

    get_terms_list(title)
    return get_terms_list(title), get_terms_list(abstract), IPC

"""
Returns the list of terms obtained from processing the given string
Params:
    string: string to be processed
"""
def get_terms_list(string):
    terms_list = []

    string_split = nltk.word_tokenize(string)
    for word in string_split:
        term = process_word(word, remove_stop_words=True, remove_numbers=True)
        if term:
            terms_list.append(word.encode('utf-8'))

    return terms_list

"""
Returns the expanded query for a given list of words using wordnet
Params:
    world_list: list of words to be expanded upon
"""
def query_expansion_wordnet(word_list):
    expanded_query = []
    for word in word_list:
        sync = wordnet.synsets(word)
        names = [l.name() for s in syncs for l in s.lemmas()]
        expanded_query += names

    expanded_query = map(make_utf, expanded_query)
    return expanded_query

"""
Returns expanded query results from Google Patent Search organised by [[list of words in title], [list of words in abstract]]
Params:
    word_list: A list of words i.e. ['washer', 'bubble']
"""
def query_expansion(word_list):
    num_response = 5    # Just taking the top 5 number of responses

    # prepare URL for ajax call
    google_url = 'https://ajax.googleapis.com/ajax/services/search/patent?v=1.0&q='
    query_string = "%20".join(str(word) for word in word_list)

    # Send the request to Google Server
    google_url += query_string
    request = urllib2.Request(google_url)
    response = urllib2.urlopen(request)

    # Process JSON
    results = json.load(response)
    response_data = results['responseData']['results'] 

    if not response_data:
        return None

    queried_results = []
    for response in response_data[:num_response]:
        # obtain list of terms from title
        title = response['titleNoFormatting'].encode('ascii', 'ignore')
        title_list = get_terms_list(title)
        # obtain list of terms from abstract
        abstract = response['content'].encode('ascii', 'ignore')
        abstract_list = get_terms_list(abstract)

        queried_results.append([title_list, abstract_list])

    #pprint.pprint(response_data)
    #print queried_results
    return queried_results

def make_utf(word):
    return word.encode('utf-8')
