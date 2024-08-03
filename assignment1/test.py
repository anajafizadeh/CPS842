import time
import inverted
import string
import stemming

def load_dictionary(dictionary_file):
    dictionary = {}
    with open(dictionary_file, 'r', encoding='utf-8') as dict_file:
        lines = dict_file.readlines()
        for line in lines[1:]:  # Skip the first line with column headers
            term, doc_freq = line.strip().split(' | ')
            dictionary[term] = int(doc_freq)
    return dictionary

def load_postings(postings_file):
    postings = []
    with open(postings_file, 'r', encoding='utf-8') as postings_list_file:
        lines = postings_list_file.read().split('\n\n')
        for entry in lines:
            if not entry.strip():
                continue
            parts = entry.strip().split('\n')
            term = parts[0].split(': ')[1]
            doc_id = int(parts[1].split(': ')[1])
            term_freq = int(parts[2].split(': ')[1])
            positions = list(map(int, parts[3].split(': ')[1][1:-1].split(', ')))
            postings.append((term, doc_id, term_freq, positions))
    return postings

def search_term(term, dictionary):
    term = term.lower()
    if term in dictionary:
        doc_freq = dictionary[term]
        return doc_freq
    else:
        return 0

def retrieve_and_display_document_info(postings, doc_id):
    result = []
    for entry in postings:
        if entry[1] == doc_id:
            result.append(entry)
    return result

def display_document_summary(doc_info, positions, term):
    text = doc_info['T'] + ' ' + doc_info.get('W', '') + ' ' + doc_info.get('B', '') + ' ' + doc_info.get('A', '')
    words = text.split()
    term_positions = set(positions)  # Convert positions to a set for efficient lookup
    summary = []

    # Context window size (number of words to include before and after the term)
    context_window = 10

    # Define a translation table to remove punctuation
    translator = str.maketrans('', '', string.punctuation)
    for i, word in enumerate(words):
        clean_word = word.translate(translator)
        if inverted.use_stemming:
            p = stemming.PorterStemmer()
            clean_word = p.stem(clean_word, 0, len(clean_word) - 1)
        if clean_word.lower() == term.lower():
            # Highlight the entire term in the summary
            summary.append(f"\033[1;31;40m{word}\033[m")  # Add ANSI escape codes for highlighting
        else:
            summary.append(word)

    # Extract the context around the highlighted term
    term_index = term_positions.pop()  # Get the index of the first occurrence of the term
    context_start = max(0, term_index - context_window)
    context_end = min(len(words), term_index + context_window + 1)
    context = ' '.join(summary[context_start:context_end])

    return context

def main():
    dictionary_file = "dictionary.txt"
    postings_file = "postings.txt"

    dictionary = load_dictionary(dictionary_file)
    postings = load_postings(postings_file)

    total_time = 0
    num_queries = 0
    documents = inverted.documents
    while True:
        term = input("Enter a term (or ZZEND to stop): ")
        if term == "ZZEND":
            break
        if inverted.use_stemming:  # checks if stemming is used
            p = stemming.PorterStemmer()
            term = p.stem(term, 0, len(term) - 1)

        start_time = time.time()
        doc_freq = search_term(term.lower(), dictionary)
        #end_time = time.time()

        if doc_freq > 0:
            print(f"Term: {term}")
            print(f"Document Frequency: {doc_freq}")
            print(f"Documents containing the term {term}:")

            doc_ids = set(entry[1] for entry in postings if entry[0] == term.lower())
            for doc_id in doc_ids:
                doc_info = documents[doc_id - 1]
                # Retrieve the positions for the term in the document
                positions = []
                for entry in retrieve_and_display_document_info(postings, doc_id):
                    if entry[0] == term.lower():
                        positions.extend(entry[3])

                # Now, positions is a list of all positions where the term occurs in the document
                summary = display_document_summary(doc_info, positions, term)

                print(f"Document ID: {doc_id}")
                print(f"Title: {doc_info['T']}")
                print(f"Term Frequency in Document: {len(positions)}")
                print(f"Positions: {positions}")
                print(f"Summary with Highlighted Term:")
                print(summary)

            end_time = time.time()
            query_time = end_time - start_time
            total_time += query_time
            num_queries += 1
            print(f"Time taken for query: {query_time:.4f} seconds")

    if num_queries > 0:
        average_time = total_time / num_queries
        print(f"Average time for queries: {average_time:.4f} seconds")

if __name__ == "__main__":
    main()

