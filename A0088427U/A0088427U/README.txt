Done as a pair: A0119646X, A0088427U

Email:
a0119646@nus.edu.sg
a0088427@nus.edu.sg

Files included: 
1. index.py: Python file for indexing the documents
2. search.py: Python file for processing a search query
3. dictionary.txt: dictionary list represented as <term> <byte position in posting list> <frequency>
4. postings.txt: posting list with continuous integers of docID where words appear

Algorithm for index.py:
1. Open file from directory
2. Get words from the file. Ignore non-alphanumeric characters such as <
3. Perform case-folding on word, i.e. convert word to lower-case. 
4. There is an option to use stop words when calling the function process_word. Set the use_stop_words flag to true. This uses the nltk English corpus stop words. This is for experimenting for Essay Question 2. If the word is a stop word, then the function returns.
5. Stem the word using the Porter stemmer provided by NLTK.
6. Add the word and docID to document dictionary.
7. Write the dictionary.txt and postings.txt

Algorithm for search.py:
1. Open query file
2. For each query, convert it to post-fix form using Shunting-Yard algorithm
3. Process the post-fix querry linearly:
	3a For each term in the query:
		if it's a term:
			stem the term
			retrieve posting list
		else if it's a binary operation, retrieve the top 2 intermediate result on the result stack and perform operation, then put result on stack
		else if it's a unary operation, retrieve the top intermediate result and perform operation, then put result on stack

4. Output the result

Note:
1. Only the merging for AND operation is done by iterating manually in order to speed up with skip pointers. In other cases, since skip pointers do not improve the performance, default python set operations were used instead to reduce code length and prevent bugs
2. Skip pointers are implemented implicitly, i.e they are offsets calculated on the fly as we iterate through the posting lists instead of fixed, offline calculated pointers generated during indexing phase

References: 
Resources from the Internet, i.e. Stack Overflow, Python documentation for python coding
Shunting-yard algorithm http://en.wikipedia.org/wiki/Shunting-yard_algorithm

