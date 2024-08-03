import stopword
from stemming import PorterStemmer
import re
from collections import defaultdict
def preprocessing(text):
    # Split text into tokens using whitespace and punctuation as delimiters
    tokens = re.findall(r'\b\w+\b', text.lower())
    return tokens

#stopword_approved = int(input("Press 1 to use stop word removal, press 0 otherwise: "))
use_stopwords = False
stopword_approved = int(input("Pick a number:\n1) Use Stopword\n2) Do not use Stopword\nAnswer: "))
if stopword_approved == 1:
    main_file = open("../cacm/reduced.txt", 'r')
    use_stopwords = True
else:
    main_file = open("../cacm/cacm.all", 'r')

documents = []
def main():
    documents = []
    current_document = None
    current_field = None
    for line in main_file:
        line = line.strip()
        if line.startswith(".I"):
            # Start a new document
            if current_document is not None:
                documents.append(current_document)
            current_document = {"I": int(line.split()[-1])}
        elif line.startswith(".T"):
            current_field = "T"
            current_document["T"] = ""
        elif line.startswith(".W"):
            current_field = "W"
            current_document["W"] = ""
        elif line.startswith(".B"):
            current_field = "B"
            current_document["B"] = ""
        elif line.startswith(".A"):
            current_field = "A"
            current_document["A"] = ""
        elif line.startswith(".K"):
            current_field = "K"
            current_document["K"] = ""
        elif line.startswith(".N"):
            current_field = "N"
            current_document["N"] = ""
        elif line.startswith(".X"):
            # Skip lines in the .X sections
            current_field = None
        elif current_field:
            # Append content to the appropriate field
            current_document[current_field] += line + ' '

    # Append the last document to the list
    if current_document is not None:
        documents.append(current_document)
    return documents

dictionary = {}
use_stemming = int(input("Pick a number:\n1) Use Stemming\n2) Do not use Stemming\nAnswer: "))

if use_stemming == 1:
    use_stemming = True
else: 
    use_stemming = False
def construct_index(documents, dictionary_file, postings_file):
    p = PorterStemmer()
    postings = []  # [postings_entry]

    # Initialize variables to keep track of postings file offset
    postings_offset = 0

    # Process each document in the 'documents' list
    for doc_id, doc_info in enumerate(documents, start=1):
        title = doc_info['T']
        abstract = doc_info.get('W', '')  # Get 'W' (abstract) if it exists, or an empty string if not
        authors = doc_info.get('A', '') # Get 'A' (author) if it exists, or an empty string if not
        date = doc_info.get('B', '') # Get 'B' (publication date) if it exists, or an empty string if not
        # Combine title and abstract if 'W' exists, otherwise use only title
        document_text = title + ' ' + abstract + ' ' + authors + ' ' + date
        if use_stemming:  # Apply stemming if use_stemming is True
            document_text = ' '.join([p.stem(word, 0, len(word)-1) for word in preprocessing(document_text)])
        else:
            document_text = ' '.join(preprocessing(document_text))
        # Split the preprocessed text into terms
        terms = document_text.split()
        # Count term frequencies in the document
        term_frequency = defaultdict(int)
        term_positions = defaultdict(list)
        for position, term in enumerate(terms):
            term_frequency[term] += 1
            term_positions[term].append(position)

        # Update the postings list
        for term, term_freq in term_frequency.items():
            if term not in dictionary:
                dictionary[term] = [0, postings_offset]
            dictionary[term][0] += 1  # Increment document frequency
            postings.append((term, doc_id, term_freq, term_positions[term]))
            postings_offset += 1
    # Sort the dictionary alphabetically
    sorted_dictionary = dict(sorted(dictionary.items()))

    # Save the dictionary in plain text
    with open(dictionary_file, 'w', encoding='utf-8') as dict_file:
        dict_file.write(" Term | Freq \n")
        for term, data in sorted_dictionary.items():
            doc_freq, postings_offset = data
            dict_file.write(f" {term} | {doc_freq}\n")

    # Save the postings list in plain text
    with open(postings_file, 'w', encoding='utf-8') as postings_list_file:
        for entry in postings:
            term, doc_id, term_freq, positions = entry
            postings_list_file.write(f"Term: {term}\n")
            postings_list_file.write(f"Document ID: {doc_id}\n")
            postings_list_file.write(f"Term Frequency: {term_freq}\n")
            postings_list_file.write(f"Positions: {positions}\n")
            postings_list_file.write("\n")

    return sorted_dictionary

# Specify the paths for the output files
dictionary_file = "dictionary.txt"
postings_file = "postings.txt"
documents = main()
dictionary = construct_index(documents, dictionary_file, postings_file)