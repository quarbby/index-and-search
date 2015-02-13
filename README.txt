Done as a pair: A0119646X

Files included: 
1. index.py: Python file for indexing the documents
2. search.py: Python file for processing a search query
3. dictionary.txt: dictionary list represented as <word> <position in posting list> <frequency>
4. postings.txt: posting list with continuous integers of docID where words appear

Algorithm for index.py:
1. Open file from directory
2. Get words from the file. Ignore non-alphanumeric characters such as <
3. Perform case-folding on word, i.e. convert word to lower-case. 
4. There is an option to use stop words when calling the function process_word. Set the use_stop_words flag to true. This uses the nltk English corpus stop words. This is for experimenting for Essay Question 2. If the word is a stop word, then the function returns.
5. Stem the word using the Porter stemmer provided by NLTK.
6. Add the word and docID to document dictionary.
7. Write the dictionary.txt and postings.txt

References: 
Resources from the Internet, i.e. Stack Overflow, for python coding
