This is the README file for submission by:
A0119646X, A0088427U and A0086894H

== General Notes about this assignment ==

Zones used from the Corpus: Title, Abstract, IPC Class
Zones used from the Query: Title, Description

General Algorithm for Indexing:
1. Read the corpus file
2. Extract the title, abstract and IPC Class
3. Perform stemming then lemmatization on the words in the title and abstract
4. Build dictionaries with the word lists of the title and the abstract. 
	4a. Add to a global title dictionary the words in the title
	4b. Add to a global abstract dictionary the words in the abstract
	4c. Build a corpus dictionary with both title and abstract word lists. 
5. Calculate the document length by using log length normalisation from the corpus dictionary. 
	i.e. We do not differentiate the words from the title and the abstract while calculating document length.
6. Add the document IPC to a dictionary of IPC Class
7. Write the dictionary and postings file: 

	a. dictionary.txt contains the IPC dictionary and term dictionary:
	- IPC dictionary written as: <ipc> <byte offset in posting file>
	- Title Term dictionary written as: <term> <byte offset in posting file> <doc freq>
	- Abstract Term dictionary written as: <term> <byte offset in posting file> <doc freq>

	b. postings.txt contains the IPC postings, document lengths and document postings: 
	- First line contains total number IPC and total number of docs tabbed spaced
	- IPC postings written as: <IPC> <list of docs> 
	- doc lengths written as: <doc> <doc_length>
	- title doc postings written as: (docID, term freq) (docID, term freq)...
	- abstract doc postings written as: (docID, term freq) (docID, term freq)...

*** ANY SUPER INTERESTING IDEAS FOR EXTRA MARKS? :) **
• We could consider Relevance feedback mentioned to us in lecture 10 - Jin

At the same time, maintain another dictionary for the IPC Class. This goes: 
<class> <docs>

General Algorithm for Searching: 
1. Read the dictionary and postings file
2. Construct a document length dictionary, document postings dictionary and IPC postings dictionary 
3. Read the query file
4. Remove the words "Relevant documents will describe", since these words repeat over the queries
5. Extract the title and description from the query file
6. Perform stemming then lemmatization on the words in the title and description
7. Performed Query Expansion on the words in the title. 
	a. Made used of Google Patent Search JSON Developer Guide
	b. Parsed the already words of the title to the Google Patent Search at https://ajax.googleapis.com/ajax/services/search/patent
	c. Recieved back the JSON object, extracted out the title and the content into lists of words 
	d. *** NOT DONE *** Add these words to the list of words we can search through the database for document IDs

*** THE RANDOM IDEA ***
*** NOT VERY SURE PLEASE HELP ON THIS ***
8. Use the LNC.LTC VSM with Weighted Zone Scoring to get out the documents as per HW3 but we don't need to rank them
i.e. 
If term in query title & doc title => doc score += score + zone title weight + zone title weight
term in query title & doc abstract => doc score += score + zone title weight + zone abstract weight
... 
10. Get the IPC Class of the documents returned then search the IPC Dictionary for more documents in the same IPC class
11. Return the top K documents in the IPC class doc list that are similar to the query (defined by cosine normalisation)

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

[X] We, A0119646X, A0088427U and A0086894H certify that we have followed the CS 3245 Information
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
Query Expansion: Google JSON Developer Guide (https://developers.google.com/patent-search/v1/jsondevguide)
Plus many Stack Overflow searches 

