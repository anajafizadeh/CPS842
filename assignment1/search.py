import math
import inverted  # Import your inverted index functions
import stemming
from nltk.corpus import wordnet # Import wordnet for query expansion

# Load documents
documents = inverted.documents  # Indexed documents

# Define whether to use stemming and stop-word removal
use_stemming = inverted.use_stemming  # Set based on user preference
if use_stemming == 1:
    use_stemming = True
else: 
    use_stemming = False
use_stopwords = inverted.use_stopwords  # Set based on user preference

def search(query):
    query = ' '.join(inverted.preprocessing(query))
    def expand_query_term(term):
        "Gets synonyms"
        synonyms = []
        for syn in wordnet.synsets(term):
            for lemma in syn.lemmas():
                synonyms.append(lemma.name())
        return synonyms

    def query_expand(query_vector, terms_to_expand):
        "Expands the query vector with synonyms"
        expanded_query_vector = query_vector.copy()

        for term in terms_to_expand:
            synonyms = expand_query_term(term)
            for synonym in synonyms:
                if use_stemming:
                    synonym = p.stem(synonym, 0, len(synonym)-1)
                if synonym.lower() not in expanded_query_vector:
                    tf = 1
                    df = search_term(synonym, dictionary)
                    if df != 0:
                        # Calculate tf-idf weight
                        tfidf = tf * math.log((total_docs / df), 10)
                        if tfidf > threshold:
                            expanded_query_vector[synonym.lower()] = tfidf  # Initialize the synonym term if not present
        return expanded_query_vector

    def remove_stopwords_from_query(query):
        # Open stopwords.txt
        with open("../cacm/stopwords.txt", "r") as f:
            stop_words = [word.lower().strip() for word in f]

        query_terms = query.lower().split()

        # Remove stopwords from the query
        query_terms = [term for term in query_terms if term not in stop_words]

        # Reconstruct the query without stopwords
        modified_query = ' '.join(query_terms)

        return modified_query

    def search_term(term, dictionary):
        "Calculates the DF"
        term = term.lower()
        if term in dictionary:
            doc_freq = dictionary[term][0]
            return doc_freq
        else:
            return 0

    # Stem the query using the stemming library
    p = stemming.PorterStemmer()

    # Preprocess the query by removing stopwords
    if use_stopwords:
        # Remove stopwords using your stop-word removal function
        query = remove_stopwords_from_query(query)

    # Create a vector representation for the query
    query_vector = {}
    # Calculate the TF (Term Frequency) weights for query terms
    query_weights = []
    total_docs = len(documents)
    dictionary = inverted.dictionary
    query_terms = []
    not_stemmed_vector = {}
    for term in query.split():
        if use_stemming:
            not_stemmed = term
            term = p.stem(term, 0, len(term)-1)
            not_stemmed_vector[term] = not_stemmed
        query_terms.append(term)

    for term in query_terms:
        query_vector[term] = query_vector.get(term, 0) + 1
    threshold = 2.6
    if use_stemming:
        threshold = 2.0
    terms_to_expand = []
    for term in query_vector:
        # Calculate the TF for the query term. 1 + log(f)
        tf = 1 + math.log((query_vector[term]), 10)
        df = search_term(term, dictionary)
        if df != 0:
            # Calculate tf-idf weight
            tfidf = tf * math.log((total_docs / df), 10)
            query_vector[term] = tfidf
            if tfidf > threshold and use_stemming:
                terms_to_expand.append(not_stemmed_vector[term])
            elif tfidf > threshold and not use_stemming:
                terms_to_expand.append(term)
        elif df == 0:
            tfidf = 0
            query_vector[term] = tfidf
        query_weights.append(tfidf)

    # Calculate the length of the query vector
    query_vector = query_expand(query_vector, terms_to_expand)

    # Initialize an empty dictionary with the same name
    filtered_query_vector = {}
    tfidf_threshold = 0.0
    # Loop through the original dictionary and filter based on the condition
    for key, value in query_vector.items():
        if value > tfidf_threshold:
            filtered_query_vector[key] = value

    query_vector = filtered_query_vector
    query_length = math.sqrt(sum(weight ** 2 for weight in query_vector.values()))
    # Calculate cosine similarity for each document
    results = []
    # Initialize the list of documents with term frequencies
    documents_with_term_freq = []
    for doc_id in range(len(documents)):
        doc_info = documents[doc_id]

        # Create a vector representation for the document
        doc_vector = {}
        doc_text = ' '.join(inverted.preprocessing(doc_info['T'] + ' ' + doc_info.get('W', '') + ' ' + doc_info.get('A', '') + ' ' + doc_info.get('N', '') + ' ' + doc_info.get('K', ''))) # Concatenate title and abstract
        doc_terms = doc_text.split()
        # Preprocess the document text
        if use_stemming:
            doc_terms = [p.stem(term, 0, len(term) - 1) for term in doc_terms]
        for term in doc_terms:
            doc_vector[term] = doc_vector.get(term, 0) + 1

        for term in doc_vector:
            tf = 1 + math.log((doc_vector[term]), 10)
            df = search_term(term, dictionary)
            if df != 0:
                tfidf = tf * math.log((total_docs / df), 10)
                doc_vector[term] = tfidf
            elif df == 0:
                tfidf = 0
                doc_vector[term] = tfidf

        # Add the document with term frequencies to the list
        doc_with_term_freq = {
            'I': doc_info['I'],  # Document ID
            'term_freq': doc_vector  # Term frequencies
        }
        documents_with_term_freq.append(doc_with_term_freq)

        # Calculate the length of the document vector
        doc_length = math.sqrt(sum(weight ** 2 for weight in doc_vector.values()))

        # Calculate the dot product between the query and document vectors
        dot_product = 0  # Initialize the dot product

        # Iterate through terms in the document vector
        for term in doc_vector:
            # Check if the term exists in the document vector
            if term in query_vector:
                # Calculate the product of term weights in the query and document vectors
                product = query_vector[term] * doc_vector[term]
                # Add the product to the dot product
                dot_product += product

        # Calculate the cosine similarity
        similarity = 0
        if query_length != 0 and doc_length != 0:
            similarity = dot_product / (query_length * doc_length)

        # Store the result
        results.append((doc_id + 1, similarity))

    # Sort results by similarity (in descending order)
    results.sort(key=lambda x: x[1], reverse=True)

    # Display the top-K relevant documents with their relevance scores
    K = 50 
    relevant_documents = []
    for i in range (min(K, len(results))):
        doc_id, similarity = results[i]
        doc_info = documents[doc_id - 1]
        relevant_documents.append({
            "Document ID": doc_id,
            "Relevance Score": similarity,
            "Title": doc_info['T'],
            "Authors": doc_info.get('A', '')
        })
    return relevant_documents

# User Interface
def ui(query):
    results = search(query)
    for i, doc in enumerate(results):
        print(f"\n{i + 1}. Document ID: {doc['Document ID']}")
        print(f"   Relevance Score: {doc['Relevance Score']}")
        print(f"   Title: {doc['Title']}")
        if doc['Authors']:
            print(f"   Authors: {doc['Authors']}")
