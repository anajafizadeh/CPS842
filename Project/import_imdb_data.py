import requests
import csv

def import_imdb_data(api_key, num_pages=25):
    base_url = 'http://www.omdbapi.com/'

    # Fetch top 250 movies
    movie_data = []
    for page in range(1, num_pages + 1):
        response = requests.get(f'{base_url}?apikey={api_key}&s=movie&type=movie&page={page}')
        data = response.json()

        if data['Response'] == 'False':
            print(f"Error: {data['Error']}")
            return []

        # Extract relevant information
        for movie in data['Search']:
            title = movie['Title']
            poster = movie['Poster']
            year = movie['Year']
            imdb_id = movie['imdbID']

            # Fetch detailed information for each movie using IMDb ID
            details_response = requests.get(f'{base_url}?apikey={api_key}&i={imdb_id}')
            details_data = details_response.json()

            if details_data['Response'] == 'False':
                print(f"Error fetching details for {title}: {details_data['Error']}")
                continue

            movie_info = {
                'title': title,
                'Poster': poster,
                'year': year,
                'rating': details_data.get('imdbRating', 'N/A'),
                'genres': details_data.get('Genre', 'N/A'),
                'director': details_data.get('Director', 'N/A'),
                'actors': details_data.get('Actors', 'N/A'),
                'director': details_data.get('Director', 'N/A'),
                'plot': details_data.get('Plot', 'N/A'),
                'age rating': details_data.get('Rated', 'N/A'),
                # Add other fields as needed
            }

            movie_data.append(movie_info)

    return movie_data

def export_to_csv(data, filename='movie_data.csv'):
    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

if __name__ == "__main__":
    api_key = 'cb8088bb'
    
    # Set the number of pages to fetch (each page has 10 movies)
    num_pages = 25
    
    movies_data = import_imdb_data(api_key, num_pages)
    
    if movies_data:
        export_to_csv(movies_data)
        print("CSV file successfully created.")
    else:
        print("No valid data fetched.")

