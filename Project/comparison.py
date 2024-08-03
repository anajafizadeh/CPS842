import csv
import pandas as pd
import numpy as np
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from surprise import accuracy

# User-Based Collaborative Filtering

def read_ratings(file_path):
    user_item_matrix = {}

    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        
        for row in reader:
            user_id, movie_id, rating = map(int, row)

            if user_id not in user_item_matrix:
                user_item_matrix[user_id] = {}

            user_item_matrix[user_id][movie_id] = rating

    return user_item_matrix

def cosine_similarity(user1, user2):
    common_movies = set(user1.keys()) & set(user2.keys())

    if not common_movies:
        return 0

    numerator = sum(user1[movie] * user2[movie] for movie in common_movies)
    denominator1 = sum(user1[movie] ** 2 for movie in common_movies) ** 0.5 
    denominator2 = sum(user2[movie] ** 2 for movie in common_movies) ** 0.5

    if denominator1 * denominator2 != 0:
        return numerator / (denominator1 * denominator2)
    else:
        return 0

def user_based_collaborative_filtering(user_item_matrix, target_user_id):
    target_user = user_item_matrix.get(target_user_id, {})
    similarities = {}

    for user_id, user in user_item_matrix.items():
        if user_id != target_user_id:
            similarities[user_id] = cosine_similarity(target_user, user)

    similar_users = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
    
    all_movie_ids = set(range(1, max(max(user_item_matrix.values(), key=lambda x: max(x, default=0)), default=0) + 1))
    rated_movies = set(target_user.keys())
    unrated_movies = all_movie_ids - rated_movies

    predictions = {}

    for movie_id in unrated_movies:
        numerator = 0
        denominator = 0

        for user_id, similarity in similar_users:
            if movie_id in user_item_matrix[user_id]:
                numerator += similarity * user_item_matrix[user_id][movie_id]
                denominator += abs(similarity)

        if denominator != 0:
            predictions[movie_id] = numerator / denominator

    return predictions

# Matrix Factorization Collaborative Filtering

def matrix_factorization_collaborative_filtering(df, target_user_id, num_recommendations=20):
    reader = Reader(line_format='user item rating', sep=',', rating_scale=(1, 5))
    data = Dataset.load_from_df(df[['userID', 'movieID', 'rating']], reader)
    trainset, testset = train_test_split(data, test_size=0.2, random_state=42)

    model = SVD(n_factors=5, lr_all=0.01, reg_all=0.02, n_epochs=100)
    model.fit(trainset)

    target_user_rated_movies = df[df['userID'] == target_user_id]['movieID'].values
    all_movie_ids = np.arange(1, 251)
    unrated_movies = np.setdiff1d(all_movie_ids, target_user_rated_movies)
    target_user_unrated_list = [(target_user_id, movie_id, 0) for movie_id in unrated_movies]
    target_user_predictions = model.test(target_user_unrated_list)

    top_recommendations = sorted(target_user_predictions, key=lambda x: x.est, reverse=True)[:num_recommendations]

    return [pred.iid for pred in top_recommendations]

# Comparison Metrics

def calculate_rmse(predictions):
    return accuracy.rmse(predictions)

def calculate_precision_recall(actual_ratings, predicted_items):
    common_items = set(actual_ratings) & set(predicted_items)
    precision = len(common_items) / len(predicted_items) if len(predicted_items) > 0 else 0
    recall = len(common_items) / len(actual_ratings) if len(actual_ratings) > 0 else 0
    return precision, recall

# Main Comparison

def main():
    file_path = 'output.csv' 
    user_item_matrix = read_ratings(file_path)

    target_user_id = int(input("Enter your userID for comparison: "))

    # User-Based Collaborative Filtering
    predictions_user_based = user_based_collaborative_filtering(user_item_matrix, target_user_id)

    # Matrix Factorization Collaborative Filtering
    df = pd.read_csv('output.csv')
    reader = Reader(line_format='user item rating', sep=',', rating_scale=(1, 5))
    data = Dataset.load_from_df(df[['userID', 'movieID', 'rating']], reader)
    trainset, testset = train_test_split(data, test_size=0.2, random_state=42)  # Define trainset
    model = SVD(n_factors=5, lr_all=0.01, reg_all=0.02, n_epochs=100)
    model.fit(trainset)  # Train the model
    predictions_matrix_factorization = model.test(testset)  # Correct way to convert testset

    # Extract item (movie) IDs from the testset
    testset_iids = [iid for (_, iid, _) in testset]

    # Comparison Metrics
    actual_ratings_matrix_factorization = np.array([pred.r_ui for pred in predictions_matrix_factorization])

    # RMSE Calculation
    # For user-based collaborative filtering
    predicted_ratings_user_based = np.array([predictions_user_based.get(movie_id, 0) for movie_id in testset_iids])
    rmse_user_based = np.sqrt(np.mean((actual_ratings_matrix_factorization - predicted_ratings_user_based)**2))
    #rmse_matrix_factorization = accuracy.rmse(predictions_matrix_factorization)
    
    print(f"RMSE for User-Based Collaborative Filtering: {rmse_user_based}")
    #print(f"RMSE for Matrix Factorization Collaborative Filtering: {rmse_matrix_factorization}")

    # Extract item (movie) IDs from the testset for Matrix Factorization
    testset_iids_matrix_factorization = [iid for (_, iid, _) in testset]
    # Precision and Recall Calculation
    precision_user_based, recall_user_based = calculate_precision_recall(actual_ratings_matrix_factorization, list(predictions_user_based.keys()))
    # Precision and Recall Calculation for Matrix Factorization Collaborative Filtering
    precision_matrix_factorization, recall_matrix_factorization = calculate_precision_recall(actual_ratings_matrix_factorization, testset_iids_matrix_factorization)

    print(f"Precision for User-Based Collaborative Filtering: {precision_user_based}")
    print(f"Recall for User-Based Collaborative Filtering: {recall_user_based}")
    #print(f"Precision for Matrix Factorization Collaborative Filtering: {precision_matrix_factorization}")
    #print(f"Recall for Matrix Factorization Collaborative Filtering: {recall_matrix_factorization}")

if __name__ == "__main__":
    main()

