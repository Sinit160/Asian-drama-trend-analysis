import os
import requests
import pandas as pd
import ast
from dotenv import load_dotenv

'''Here I load the raw dataset, inspect missing values and duplicates,
fill missing overview values, preserve unrated dramas (vote_count = 0),
convert release dates to a datetime format, remove unnecessary columns,
map TMDB genre IDs to readable genre names, and save the cleaned dataset
as data/cleaned_dramas.csv for analysis.'''

load_dotenv()
Data = os.getenv('TMDB_API_KEY')

df = pd.read_csv('data/raw_dramas.csv')

print(df.isnull().sum())
df["overview"] = df["overview"].fillna("No overview available")
print((df["vote_count"] == 0).sum())  # 10 values kept for better analysis
print(df.duplicated().sum())
print(df["id"].duplicated().sum())    # 0 duplicates in both cases

df["first_air_date"] = pd.to_datetime(df["first_air_date"])
df = df.drop(columns=['backdrop_path', 'poster_path'])

# Map genre IDs to genre names
genre_url = "https://api.themoviedb.org/3/genre/tv/list"
genre_response = requests.get(genre_url, params={"api_key": Data})
genre_data = genre_response.json()
genre_lookup = {genre["id"]: genre["name"] for genre in genre_data["genres"]}

df["genre_names"] = df["genre_ids"].apply(
    lambda x: ", ".join(genre_lookup.get(i, "Unknown") for i in ast.literal_eval(x))
)
df["genre_ids"] = df["genre_ids"].apply(
    lambda x: ", ".join(map(str, ast.literal_eval(x)))
)

df.to_csv('data/cleaned_dramas.csv', index=False)
print(f"Cleaned dataset saved with {len(df)} rows")