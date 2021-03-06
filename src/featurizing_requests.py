

import pandas as pd
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


movies_df = pd.read_csv("../data/movies.dat", sep='::', names=["request_movie_id", "title", "genres"])
movies_df['year'] = movies_df['title'].str[-5:-1]
movies_df['title'] = movies_df['title'].str[:-7]
movies_df['genres'] = movies_df['genres'].str.split('|')
movies_df['title']=movies_df['title'].apply(lambda x: x.split(',')[1].lstrip(' ') + " "+ x.split(',')[0] if ', The' in x else x)

users_df = pd.read_csv("../data/users.dat", sep='::', names=["request_id", "gender", "age", 'number', 'id'])
users_df['gender'] = users_df['gender'].map({'F': 1, 'M': 0})

#merging movie_metadata with movies_df
movie_metadata = pd.read_csv('../data/movies_metadata.csv')
movies_metadata_df = movies_df.merge(movie_metadata, left_on='title', right_on='title', how='left')
movies_metadata_df = movies_metadata_df.drop_duplicates(subset='title', keep='first')

from sklearn.preprocessing import MultiLabelBinarizer
mlb = MultiLabelBinarizer()


requests_df = pd.read_csv('../data/requests.csv')


requests_RF_df = requests_df.copy()
requests_RF_df = requests_RF_df.merge(users_df, how='left', left_on='user', right_on='request_id')
requests_RF_df = pd.merge(requests_RF_df, movies_metadata_df, how='left', left_on='movie', right_on='request_movie_id')

requests_RF_df['genres_x'].fillna(0, inplace=True)
genres = list(requests_RF_df['genres_x'])
genres = [x if x else ['Other'] for x in genres]
requests_RF_df['genres'] = genres
mlb.fit(requests_RF_df['genres'])
requests_RF_df[mlb.classes_] = mlb.transform(requests_RF_df['genres'])
mlb.fit(requests_RF_df['genres'])
requests_RF_df[mlb.classes_] = mlb.transform(requests_RF_df['genres'])



requests_RF_df.drop(['user', 'movie', 'request_id', 'id_x', 'genres_x', 'genres', 'request_movie_id', 'title', 'genres_x', 'adult', 'belongs_to_collection',
         'genres_y', 'homepage', 'id_y', 'imdb_id', 'original_language', 'original_title', 'overview', 'poster_path',
         'production_companies', 'production_countries', 'release_date', 'spoken_languages', 'status', 'tagline', 'video'], axis=1, inplace=True)
requests_RF_df.fillna(requests_RF_df.median(), inplace=True)

from joblib import dump, load

RF_Model = load('../data/RF_model.joblib')
requests_RF_pred = RF_Model.predict(requests_RF_df)


requests_matrix_preds = pd.read_csv('../data/test1_results.csv')

final_preds = requests_matrix_preds.copy()
final_preds['RF_preds'] = requests_RF_pred
final_preds['prediction'].fillna(final_preds['RF_preds'], inplace=True)
final_preds.drop('RF_preds', axis=1, inplace=True)
final_preds.rename(columns={'prediction': 'rating'}, inplace=True)
print(final_preds)
final_preds.to_csv('../data/Netflix_prediction3', index=False)