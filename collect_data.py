import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
Data = os.getenv('TMDB_API_KEY')

url = 'https://api.themoviedb.org/3/discover/tv'
params = {
    'api_key': Data,
    'with_origin_country': 'KR'
}

response = requests.get(url, params=params)
print(response.json())


