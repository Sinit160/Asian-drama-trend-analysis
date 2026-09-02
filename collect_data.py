import os
import requests
import pandas as pd
import ast
from dotenv import load_dotenv
# Step 1
'''here i  loaded the TMDB API key from the environment, requested the
20 most popular pages of Korean TV dramas in the Drama genre using TMDB's
pagination, combine all results into a single pandas DataFrame, and saved
the raw dataset as data/raw_dramas.csv for later cleaning and analysis.'''
load_dotenv()
Data = os.getenv('TMDB_API_KEY')

url = 'https://api.themoviedb.org/3/discover/tv'
dramas = []
params = {
    'api_key': Data,
    'with_origin_country': 'KR',
    'with_genres' : '18',
    'sort_by': 'popularity.desc',
    'page' : 2,
}

# loop through(pagination)
for page in range (1,21):
    params['page'] = page
    response = requests.get(url, params=params)
    results = response.json()['results']
    dramas.extend(results)
    #print(f"collected pages:{page}")

#print(len(dramas))
#print(dramas[0])

df = pd.DataFrame(dramas)
os.makedirs("data", exist_ok=True)

df.to_csv("data/raw_dramas.csv")

# step 2 ( cleaning the data)
'''here we load the raw dataset, inspects missing values and duplicates,
fills missing overview values, preserve unrated dramas (vote_count = 0),
convert release dates to a datetime format, remove unnecessary columns,
map TMDB genre IDs to readable genre names, and save the cleaned dataset
as `data/cleaned_dramas.csv` for analysis.'''
df = pd.read_csv('data/raw_dramas.csv', index=False)
df.info()# just to inspect the data
print(df.isnull().sum())
df["overview"] = df["overview"].fillna("No overview available")
print(df["overview"].isna().sum())
print((df["vote_count"] == 0).sum()) # i have 10 values there but i decided to keep for better analysis
print(df.duplicated().sum())
print(df["id"].duplicated().sum()) # i have 0 duplicates in both cases
df["first_air_date"] = pd.to_datetime(df["first_air_date"])
print(df["first_air_date"].dtype)
df = df.drop(columns=['Unnamed: 0','backdrop_path', 'poster_path'])
print(df.columns)

# i forgot to map the gerne ids ( let do that now)
# Step 2.5 - Map genre IDs to genre names

genre_url = "https://api.themoviedb.org/3/genre/tv/list"
genre_response = requests.get(genre_url, params={"api_key": Data})
genre_data = genre_response.json()
# Create {id: name} lookup dictionary
genre_lookup = {
    genre["id"]: genre["name"]
    for genre in genre_data["genres"]
}
# Convert genre_ids into readable genre names
df["genre_names"] = df["genre_ids"].apply(
    lambda x: [genre_lookup.get(i, "Unknown") for i in ast.literal_eval(x)]
)
# Quick check
print(df[["genre_ids", "genre_names"]].head())
df.to_csv('data/cleaned_dramas.csv ', index=False)




