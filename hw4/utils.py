#!/usr/bin/python

'''
General utility functions such as language parsing and XML parsing
'''

import nltk
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

from xml.dom import minidom

import urllib2
import json
import pprint

stop_words = set(nltk.corpus.stopwords.words('english'))
stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

def process_word(word, remove_stop_words=False, remove_numbers=False):
    word = filter(str.isalnum, word)    # Remove non alpha-numeric character

    word = word.lower()

    if remove_stop_words and word in stop_words:
            return 

    if remove_numbers and word.isdigit():
            return

    word = stemmer.stem(word)
    word = lemmatizer.lemmatize(word)

    if (len(word) < 3):
        return
    return word

# Input: Query File Name 
# Output: A List of processed words from the title and description of the query
def XML_query_parser(filename):
	dom = minidom.parse(filename)
	title = dom.getElementsByTagName('title')[0].firstChild.nodeValue.strip().encode('utf-8')
	description = dom.getElementsByTagName('description')[0].firstChild.nodeValue.strip().encode('utf-8')

	description = remove_words(description)

	query_title_list = get_word_list(title)
	query_desc_list = get_word_list(description)

	return query_title_list, query_desc_list

# Remove the words "Relevant documents will describe" from the description
def remove_words(description):
	return description.replace("Relevant documents will describe", "")

# Input: Corpus file name
# Output: List of processed words from title, abstract and the IPC number
def XML_corpus_parser(filename):
	title = ""
	abstract = ""
	IPC = ""

	dom = minidom.parse(filename)
	for node in dom.getElementsByTagName('str'):
		if node.firstChild is not None:
			tag = node.attributes.item(0).value.strip()
			value = node.firstChild.nodeValue.strip().encode('utf-8')

			if tag == 'Title': 
				title = value
			elif tag == 'Abstract':
				abstract = value
			elif tag == "IPC Class":
				IPC = value

	get_word_list(title)
	return [get_word_list(title), get_word_list(abstract), IPC]

def get_word_list(string):
	word_list = []

	string_split = nltk.word_tokenize(string)
	for word in string_split:
		word = process_word(word, remove_stop_words=True, remove_numbers=True)
		if word:
			word_list.append(word.encode('utf-8'))

	return word_list

# Input: A list of words
# Output: Query expansion from wordnet 
def query_expansion_wordnet(word_list):
    expanded_query = []
    for word in word_list:
        sync = wordnet.synsets(word)
        names = l.name() for s in syncs for l in s.lemmas()]
        expanded_query += names

    expanded_query = map(make_utf, expanded_query)
    return expanded_query


# Input: A list of words i.e. ['washer', 'bubble']
# Output: Queried results from Google Patent Search organised by [[list of words in title], [list of words in abstract]] 
def query_expansion(word_list):
	num_response = 5	# Just taking the top 5 number of responses

	google_url = 'https://ajax.googleapis.com/ajax/services/search/patent?v=1.0&q='
	query_string = "%20".join(str(word) for word in word_list)

	# Send the request to Google Server
	google_url += query_string
	request = urllib2.Request(google_url)
	response = urllib2.urlopen(request)

	# Process JSON
	results = json.load(response)
	response_data = results['responseData']['results'] 

	if response_data is None:
		return

	count = 0
	queried_results = []
	for response in response_data:
		if count > num_response:
			break

		title = response['titleNoFormatting'].encode('ascii', 'ignore')
		title_list = get_word_list(title)

		abstract = response['content'].encode('ascii', 'ignore')
		abstract_list = get_word_list(abstract)

		title_and_query = [title_list, abstract_list]
		queried_results.append(title_and_query)

		count += 1


	#pprint.pprint(response_data)

	#print queried_results

	return queried_results

def make_utf(word):
    return word.encode('utf-8')
