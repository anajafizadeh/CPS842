import pandas as pd
import numpy as np
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from surprise import accuracy

# Assuming you have a pandas DataFrame with columns: 'userID', 'movieID', 'rating'
# Replace [your_dataframe] with the actual name of your DataFrame
# Example: df = pd.read_csv('your_ratings_data.csv', skiprows=2)
# Make sure your DataFrame has columns 'userID', 'movieID', and 'rating'
df = pd.read_csv('output.csv')

# Create a Surprise Dataset using the Reader class
reader = Reader(line_format='user item rating', sep=',', rating_scale=(1, 5))
data = Dataset.load_from_df(df[['userID', 'movieID', 'rating']], reader)

# Split the dataset into training and testing sets
trainset, testset = train_test_split(data, test_size=0.2, random_state=42)

# Use the SVD algorithm for matrix factorization
model = SVD(n_factors=5, lr_all=0.01, reg_all=0.02, n_epochs=100)
model.fit(trainset)

# Now, you can use the trained model to predict ratings for a target user
target_user_id = 1  # Replace with the desired target user ID
target_user_rated_movies = df[df['userID'] == target_user_id]['movieID'].values

# Create an array of all movie IDs
all_movie_ids = np.arange(1, 251)  # Assuming movie IDs range from 1 to 250

# Remove the movies that the user has already rated
unrated_movies = np.setdiff1d(all_movie_ids, target_user_rated_movies)

# Create a list of tuples for unrated movies for the target user
target_user_unrated_list = [(target_user_id, movie_id, 0) for movie_id in unrated_movies]

# Make predictions for the unrated movies
target_user_predictions = model.test(target_user_unrated_list)

# Get top N recommendations for the target user
num_recommendations = 20  # Adjust as needed
top_recommendations = sorted(target_user_predictions, key=lambda x: x.est, reverse=True)[:num_recommendations]

print("Top {} recommended movies for user {}: {}".format(num_recommendations, target_user_id, [pred.iid for pred in top_recommendations]))
