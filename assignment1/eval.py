from search import search

# Load the queries from the query file
# Load qrels.txt
def load_qrels(qrels_file):
    qrels = {}
    with open(qrels_file, "r") as file:
        for line in file:
            parts = line.strip().split()
            query_id = int(parts[0])
            doc_id = int(parts[1])
            if query_id not in qrels:
                qrels[query_id] = []
            qrels[query_id].append(doc_id)
    return qrels

# Load queries from query.txt
def load_queries(query_file):
    queries = {}
    current_query = None
    with open(query_file, "r") as file:
        for line in file:
            line = line.strip()
            if line.startswith(".I"):
                if current_query is not None:
                    queries[current_query["query_id"]] = " ".join(current_query["text"])
                query_id = int(line.split()[1])
                current_query = {"query_id": query_id, "text": []}
            elif line.startswith(".W") or line.startswith(".N"):
                continue
            else:
                current_query["text"].append(line)
    if current_query is not None:
        queries[current_query["query_id"]] = " ".join(current_query["text"])
    return queries

# Calculate Average Precision (AP) for a query
def calculate_average_precision(retrieved_results, relevant_docs):
    num_retrieved = 0
    num_relevant_retrieved = 0
    precision_at_k = []
    
    for i, doc_id in enumerate(retrieved_results):
        if doc_id in relevant_docs:
            num_relevant_retrieved += 1
            precision_at_k.append(num_relevant_retrieved / (i + 1))
    
    if not precision_at_k:
        return 0.0
    
    return sum(precision_at_k) / len(relevant_docs)

# Evaluate the IR system
def evaluate_ir_system(query_file, qrels_file):
    queries = load_queries(query_file)
    qrels = load_qrels(qrels_file)

    mean_average_precision = 0
    average_r_precision = 0

    for query_id, query_text in queries.items():
        retrieved_results = [doc["Document ID"] for doc in search(query_text)]
        relevant_docs = qrels.get(query_id, [])

        # Calculate Average Precision (AP) for this query
        ap = calculate_average_precision(retrieved_results, relevant_docs)
        
        # Update mean_average_precision and average_r_precision
        mean_average_precision += ap
        if len(relevant_docs) > 0:
            r_precision = len(set(retrieved_results).intersection(set(relevant_docs))) / len(relevant_docs)
            average_r_precision += r_precision

    num_queries = len(queries)
    mean_average_precision /= num_queries
    average_r_precision /= num_queries

    return mean_average_precision, average_r_precision

# Usage
query_file = '../cacm/query.text'
qrels_file = '../cacm/qrels.text'
mean_average_precision, average_r_precision = evaluate_ir_system(query_file, qrels_file)

print(f"Mean Average Precision (MAP): {mean_average_precision}")
print(f"Average R-Precision: {average_r_precision}")

