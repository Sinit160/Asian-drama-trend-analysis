import os
import requests
import pandas as pd
from dotenv import load_dotenv
# Stage 1
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
    print(f"collected pages:{page}")

print(len(dramas))
print(dramas[0])

df = pd.DataFrame(dramas)
os.makedirs("data", exist_ok=True)

df.to_csv("data/raw_dramas.csv")


