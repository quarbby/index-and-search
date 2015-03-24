This is the README file for submission by:
A0119646X, A0088427U and 

== General Notes about this assignment ==

Zones used from the Corpus: Title, Abstract, IPC Class
Zones used from the Query: Title, Description

General Algorithm for Indexing:
1. Read the corpus file
2. Extract the title, abstract and IPC Class
3. Perform stemming then lemmatization on the words in the title and abstract
4. Build a corpus dictionary with the merged word lists of the title and the abstract. 
5. Calculate the document length by using log length normalisation from the corpus dictionary. 
6. Add the document IPC to a dictionary of IPC Class
7. Write the dictionary and postings file: 

	a. dictionary.txt contains the IPC dictionary and term dictionary:
	- IPC dictionary written as: <ipc> <byte offset in posting file>
	- Term dictionary written as: <term> <byte offset in posting file> <doc freq>

	b. postings.txt contains the IPC postings, document lengths and document postings: 
	- First line contains total number IPC and total number of docs tabbed spaced
	- IPC postings written as: <IPC> <list of docs> 
	- doc lengths written as: <doc> <doc_length>
	- doc postings written as: (docID, term freq) (docID, term freq)...

*** ANY SUPER INTERESTING IDEAS FOR EXTRA MARKS? :) **

At the same time, maintain another dictionary for the IPC Class. This goes: 
<class> <docs>

General Algorithm for Searching: 
1. Read the dictionary and postings file
2. Construct a document length dictionary, document postings dictionary and IPC postings dictionary 
3. Read the query file
4. Remove the words "Relevant documents will describe", since these words repeat over the queries
5. Extract the title and description from the query file
6. Perform stemming then lemmatization on the words in the title and description

*** THE RANDOM IDEA ***
7. Perform Query Expansion on the words in the title (Optional. I don't know how to do them either)
8. Use the LNC.LTC VSM to get out the documents as per HW3 but we don't rank them
9. Get the IPC Class of the documents returned then search the IPC Dictionary for more documents in the same IPC class
10. Return the top K documents in the IPC class doc list that are similar to the query (defined by cosine normalisation)

== Files included with this submission ==

Modified files: 

README.txt -- This file, with general comments about the assignment

index.py -- File for indexing the PatSnap Corpus
search.py -- File for searching the PatSnap Corups when given a query
utils.py -- File with general utility functions such as stemming and lemmatizing the words

dictionary.txt -- The dictionary file of indexed PatSnap corpus 
postings.txt -- The postings file of indexed PatSnap corpus

== Statement of group work ==

Please initial one of the following statements.

[X] We, A0119646X, A0088 427U, and A certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

I suggest that I should be graded as follows:

<Please fill in>

== References ==

<Please list any websites and/or people you consulted with for this
assignment and state their role>
A general structure of the program is taken from our previous homework assignments 2 and 3.
Python MiniDom for XML parsing: https://wiki.python.org/moin/MiniDom
NLTK Documentation for Porter Stemmer and Word Net Lemmatizer 
Plus many Stack Overflow searches 

