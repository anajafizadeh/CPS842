import csv

# Function to read the ratings CSV file and create a user-item matrix
def read_ratings(file_path):
    user_item_matrix = {}

    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        
        # Skip the first two header rows
        # Remove one of these two lines if you only have 1 header
        next(reader)
        next(reader)
        
        for row in reader:
            user_id, movie_id, rating = map(int, row)

            if user_id not in user_item_matrix:
                user_item_matrix[user_id] = {}

            user_item_matrix[user_id][movie_id] = rating

    return user_item_matrix

# Function to calculate cosine similarity between two users
def cosine_similarity(user1, user2):
    
    # Common movies rated by user1 & user2
    common_movies = set(user1.keys()) & set(user2.keys())
    
    if not common_movies:
        return 0
    
    numerator = sum(user1[movie] * user2[movie] for movie in common_movies)
    # User1 normalized ratings
    denominator1 = sum(user1[movie] ** 2 for movie in common_movies) ** 0.5 
    # User2 normalized ratings
    denominator2 = sum(user2[movie] ** 2 for movie in common_movies) ** 0.5
    if denominator1 * denominator2 != 0:
        return numerator / (denominator1 * denominator2)
    # Special case where user1 has not rated X and have no common movies with user2 except for X
    else:
        return 0

# Function to perform user-based collaborative filtering
def user_based_collaborative_filtering(user_item_matrix, target_user_id):
    target_user = user_item_matrix.get(target_user_id, {})
    
    # Calculate similarity between the target user and all other users
    similarities = {}
    for user_id, user in user_item_matrix.items():
        if user_id != target_user_id:
            similarities[user_id] = cosine_similarity(target_user, user)
    
    # Sort users by similarity in descending order
    similar_users = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
    
    # Find unrated movies by the target user
    all_movie_ids = set(range(1, max(max(user_item_matrix.values(), key=lambda x: max(x, default=0)), default=0) + 1))
    rated_movies = set(target_user.keys())
    unrated_movies = all_movie_ids - rated_movies

    # Predict ratings for unrated movies based on similar users
    predictions = {}
    for movie_id in unrated_movies:
        numerator = 0
        denominator = 0
        
        for user_id, similarity in similar_users:
            # Check if the movie_id is present in the user's ratings
            if movie_id in user_item_matrix[user_id]:
                numerator += similarity * user_item_matrix[user_id][movie_id]
                denominator += abs(similarity)
        
        if denominator != 0:
            predictions[movie_id] = numerator / denominator
    
    return predictions

# Usage
file_path = 'output.csv' 
user_item_matrix = read_ratings(file_path)

# Input the target_user_id
target_user_id = int(input("Enter your userID: "))
predictions = user_based_collaborative_filtering(user_item_matrix, target_user_id)

# Print the recommendations
# TO DO: Modify to get the top K
print(f"Recommendations for User {target_user_id}:")
K = 20 # Change K based on youe preference
count = 1
for movie_id, rating in sorted(predictions.items(), key=lambda x: x[1], reverse=True):
    if count <= K:
        count += 1
        print(f"Movie {movie_id}: {rating:.2f}")
