import os
import requests
import pandas as pd
from dotenv import load_dotenv

'''Here I load the TMDB API key from the environment, request the
20 most popular pages of Korean TV dramas in the Drama genre using TMDB's
pagination, combine all results into a single pandas DataFrame, and save
the raw dataset as data/raw_dramas.csv for later cleaning and analysis.'''

load_dotenv()
Data = os.getenv('TMDB_API_KEY')

url = 'https://api.themoviedb.org/3/discover/tv'
dramas = []
params = {
    'api_key': Data,
    'with_origin_country': 'KR',
    'with_genres': '18',
    'sort_by': 'popularity.desc',
    'page': 2,
}

for page in range(1, 21):
    params['page'] = page
    response = requests.get(url, params=params)
    results = response.json()['results']
    dramas.extend(results)

df = pd.DataFrame(dramas)
os.makedirs("data", exist_ok=True)
df.to_csv("data/raw_dramas.csv", index=False)

print(f"Collected {len(df)} dramas and saved to data/raw_dramas.csv")