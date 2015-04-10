This is the README file for submission by:
A0119646X, A0088427U and A0086894H

== General Notes about this assignment ==

Zones used from the Corpus: Title, Abstract, IPC Class
Zones used from the Query: Title, Description

General Algorithm for Indexing:
1. Read the corpus file
2. Extract the title, abstract, IPC Class and family member from each XML document.
3. Perform stemming then lemmatization on the words in the title and abstract.
4. Build dictionaries with the word lists of the title and the abstract. 
	4a. Add to a global title dictionary the words in the title
	4b. Add to a global abstract dictionary the words in the abstract
5. Calculate the necessary vector lengths by using log length normalisation from the corpus dictionary. 
	a. Calculate the document length for each document
	b. Calculate title length for each document 
	c. Calculate absctract length for each document
	d. Index the lengths calculated to be written into the dictionary in Step 8.
6. Add the document IPC to a dictionary of IPC Class, with the document ID as the key. 
7. Add the list of family members (one document may have multiple family members, i.e. related XML documents) to a dictionary of family member, with the document ID as the key. 
8. Write the dictionary and postings file: 

	a. main dictionary:
	    <docId>:<IPC>, ...                  // first line lists out docId and their respective IPC class
	    <docId>:<document length>, ...      // second line lists out document length calculated using all terms in document
	    <docId>:<document length>, ...      // third line lists out document length of title zone
	    <docId>:<document length>, ...      // fourth line lists out document length of abstract zone
	    title:dictionary_title.txt          // title:<dictionary filename for title zone>
	    abstract:dictionary_abstract.txt    // abstract:<dictionary filename for abstract zone>
	    IPC:dictionary_IPC.txt              // IPC:<dictionary filename for IPC class>
	    family_member: family_memebrs.txt   // family_member:<dictionary filename for family members>

	b. zone dictionary for title and abstract:
	    <term> <byte offset in postings file> <df>
	    ...
	c. zone dictionary for IPC:
	    <term> <byte offset in postings file>
	    ...
	d. main postings file:
	    title:postings_title.txt            // title:<postings filename for title zone>
	    abstract:postings_abstract.txt      // abstract:<postings filename for abstract zone>
	    IPC:postings_IPC.txt                // IPC:<postings filename for abstract zone>

	e. zone postings file for title and abstract:
	    <docId>:<tf>, ...                   // list out docId:tf pair
	    ...
	f. zone postings file for IPC:
	    <docId>, ...                        // list of docIds


General Algorithm for Searching: 
1. Read the dictionary and postings files 
	a. Load all the zone dictionaries: 'title', 'abstract', 'IPC'
2. Read the query file
3. Remove the words "Relevant documents will describe", since these words repeat over the queries
4. Extract the title and description from the query file
5. Perform stemming then lemmatization on the words in the title and description
6. Performed Query Expansion on the words in the title. 
	a. Made used of Google Patent Search JSON Developer Guide
	b. Parsed the already words of the title to the Google Patent Search at https://ajax.googleapis.com/ajax/services/search/patent
	c. Recieved back the JSON object, extracted out the title and the content into lists of words 
7. Get document scores by cosine normalisation and zone weighting
	a. Weight for score from query title & document title = 4.0 
	b. Weight for score from query description & document title = 1.0
	c. Weight for score from query title & document abstract = 4.0
	d. Weight for score from query description & document abstract = 1.0
	e. These zone weights are set by emprical values. 
8. Filter documents
	a. Rank the results by their cosine scores, from the highest to the lowest. 
	b. Pick the top 10 results and find their IPC class.
	c. Find the most common IPC class among the top 10 results.
	d. Return documents which has the most common IPC class and are in the top 10 results. This is used because IPC class is manually set for the XML patent document, so they should more correctly reflect the patent document. 

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

