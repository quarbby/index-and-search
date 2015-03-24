#!/usr/bin/python

'''
General utility functions such as language parsing and XML parsing
'''

import nltk
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer

from xml.dom import minidom

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