import os
import requests
import pandas as pd
import ast
import sqlite3
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import seaborn as sns

# day 1
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

df.to_csv("data/raw_dramas.csv", index=False)

# Day 2
# step 2 ( cleaning the data)
'''here we load the raw dataset, inspects missing values and duplicates,
fills missing overview values, preserve unrated dramas (vote_count = 0),
convert release dates to a datetime format, remove unnecessary columns,
map TMDB genre IDs to readable genre names, and save the cleaned dataset
as `data/cleaned_dramas.csv` for analysis.'''
df = pd.read_csv('data/raw_dramas.csv')
df.info()# just to inspect the data
print(df.isnull().sum())
df["overview"] = df["overview"].fillna("No overview available")
print(df["overview"].isna().sum())
print((df["vote_count"] == 0).sum()) # i have 10 values there but i decided to keep for better analysis
print(df.duplicated().sum())
print(df["id"].duplicated().sum()) # i have 0 duplicates in both cases
df["first_air_date"] = pd.to_datetime(df["first_air_date"])
print(df["first_air_date"].dtype)
df = df.drop(columns=['backdrop_path', 'poster_path'])
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
    lambda x: ", ".join(
        genre_lookup.get(i, "Unknown")
        for i in ast.literal_eval(x)
    )
)
# Quick check
print(df[["genre_ids", "genre_names"]].head())
# Convert genre_ids from "[80, 18, 9648]" to "80, 18, 9648"
df["genre_ids"] = df["genre_ids"].apply(
    lambda x: ", ".join(map(str, ast.literal_eval(x)))
)
# Check
print(df[["genre_ids", "genre_names"]].head())

df.to_csv('data/cleaned_dramas.csv', index=False)

# day 3
# create an sqlite database
'''Here i am creating an SQLite database, loading the cleaned DataFrame into an
SQL table named dramas, and verifying that all rows were successfully imported.'''

conn = sqlite3.connect("kdramas.db")
df.to_sql("dramas", conn, if_exists="replace", index=False) # Load DataFrame into SQL
query = "SELECT COUNT(*) AS total_dramas FROM dramas;" # check
print(pd.read_sql_query(query, conn))

# Create folder for saved charts
os.makedirs("outputs", exist_ok=True)

# Apply one theme to every chart
sns.set_theme(style="whitegrid", palette="deep")

# query 1
'''This query counts how many dramas were released each year.'''
q1 = pd.read_sql_query("""
SELECT
    strftime('%Y', first_air_date) AS release_year,
    COUNT(*) AS total_dramas
FROM dramas
GROUP BY release_year
ORDER BY release_year;
""", conn)
 # chart 
plt.figure(figsize=(10,5))

sns.lineplot(
    data=q1,
    x="release_year",
    y="total_dramas",
    marker="o",
    linewidth=2.5
)

plt.title("Korean Dramas Released by Year", fontsize=15, weight="bold")
plt.xlabel("Release Year")
plt.ylabel("Number of Dramas")

plt.tight_layout()
plt.savefig("outputs/dramas_by_year.png", dpi=300)
plt.show()

print(f"interpretation : The chart shows how the number of popular Korean dramas changed over time. Higher counts in recent years suggest increased production.")

#query 2
'''This query calculates the average TMDB rating for dramas released each year.'''

q2 = pd.read_sql_query("""
SELECT
    strftime('%Y', first_air_date) AS release_year,
    ROUND(AVG(vote_average),2) AS average_rating
FROM dramas
GROUP BY release_year
ORDER BY release_year;
""", conn)
# cahrt 2
plt.figure(figsize=(10,5))

sns.lineplot(
    data=q2,
    x="release_year",
    y="average_rating",
    marker="o",
    linewidth=2.5
)

plt.title("Average TMDB Rating by Release Year", fontsize=15, weight="bold")
plt.xlabel("Release Year")
plt.ylabel("Average Rating")

plt.tight_layout()
plt.savefig("outputs/average_rating_by_year.png", dpi=300)
plt.show()

# Check whether Romance exists in TMDB's TV genre list( put it in readme cause it is a limitation)
print(genre_lookup)
print("Romance exists:", "Romance" in genre_lookup.values())

print("Interpretation: Drama appears most frequently, while genres such as " \
"Crime and Mystery appear less often. TMDB's TV genre taxonomy does not include a standalone Romance category, so romance-themed Korean dramas are typically classified under Drama or other genres.")

# Check vote_count distribution to choose a reasonable threshold
print(df["vote_count"].describe())

# query 3
'''This query finds the ten highest-rated dramas in the dataset.'''

q3 = pd.read_sql_query("""
SELECT
    name,
    vote_average,
    vote_count
FROM dramas
WHERE vote_count >= 20
ORDER BY vote_average DESC
LIMIT 10;
""", conn)

# chart 3
plt.figure(figsize=(10,6))

ax = sns.barplot(
    data=q3,
    x="vote_average",
    y="name"
)

plt.title("Top 10 Highest-Rated Korean Dramas", fontsize=15, weight="bold")
plt.xlabel("TMDB Rating")
plt.ylabel("")

# Add value labels
for container in ax.containers:
    ax.bar_label(container, fmt="%.1f", padding=4)

plt.tight_layout()
plt.savefig("outputs/top_rated_dramas.png", dpi=300)
plt.show()
print("Interpretation: Average ratings remain relatively stable across years." \
" Earlier years contain far fewer dramas, so individual outliers have a much larger effect on the yearly average than recent years.")
# query 4
'''This query finds the ten dramas with the highest popularity scores.'''

q4 = pd.read_sql_query("""
SELECT
    name,
    popularity
FROM dramas
ORDER BY popularity DESC
LIMIT 10;
""", conn)

# chart 4
plt.figure(figsize=(10,6))

ax = sns.barplot(
    data=q4,
    x="popularity",
    y="name"
)

plt.title("Top 10 Most Popular Korean Dramas", fontsize=15, weight="bold")
plt.xlabel("Popularity Score")
plt.ylabel("")

for container in ax.containers:
    ax.bar_label(container, fmt="%.0f", padding=4)

plt.tight_layout()
plt.savefig("outputs/top_popular_dramas.png", dpi=300)
plt.show()

print(f"interpretation:Popularity scores highlight which dramas generated the greatest overall interest on TMDB.")

# query 5
'''This query counts how many dramas contain each major genre.'''
q5 = pd.read_sql_query("""
SELECT 'Drama' AS genre, COUNT(*) AS total
FROM dramas
WHERE genre_names LIKE '%Drama%'

UNION ALL

SELECT 'Comedy', COUNT(*)
FROM dramas
WHERE genre_names LIKE '%Comedy%'

UNION ALL

SELECT 'Romance', COUNT(*)
FROM dramas
WHERE genre_names LIKE '%Romance%'

UNION ALL

SELECT 'Mystery', COUNT(*)
FROM dramas
WHERE genre_names LIKE '%Mystery%'

UNION ALL

SELECT 'Crime', COUNT(*)
FROM dramas
WHERE genre_names LIKE '%Crime%'

UNION ALL

SELECT 'Action & Adventure', COUNT(*)
FROM dramas
WHERE genre_names LIKE '%Action & Adventure%'

ORDER BY total DESC;
""", conn)

# chart 5
plt.figure(figsize=(9,5))

ax = sns.barplot(
    data=q5,
    x="genre",
    y="total"
)

plt.title("Most Common Genres in Popular Korean Dramas", fontsize=15, weight="bold")
plt.xlabel("")
plt.ylabel("Number of Dramas")
plt.xticks(rotation=30)

for container in ax.containers:
    ax.bar_label(container, padding=3)

plt.tight_layout()
plt.savefig("outputs/genre_frequency.png", dpi=300)
plt.show()
print(f"interpretation: Drama appears most frequently, while genres like Crime and Mystery appear less often, showing that many popular Korean dramas combine drama with other genres.")
conn.close() # close it
