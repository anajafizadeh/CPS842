import search

def main():
    "Provides the user interface for searching queries"
    while True:
        query = input("Enter your query (or ZZEND to stop): ")
        if query == "ZZEND":
                break
        search.ui(query)
        
if __name__ == "__main__":
    main()
    