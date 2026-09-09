import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

'''Here I load the cleaned dataset into an SQLite database, run analysis
queries, and generate charts summarizing trends in Korean dramas.'''

df = pd.read_csv('data/cleaned_dramas.csv')

conn = sqlite3.connect("kdramas.db")
df.to_sql("dramas", conn, if_exists="replace", index=False)

os.makedirs("outputs", exist_ok=True)
sns.set_theme(style="whitegrid", palette="deep")

# Query 1: dramas released per year
q1 = pd.read_sql_query("""
    SELECT strftime('%Y', first_air_date) AS release_year, COUNT(*) AS total_dramas
    FROM dramas GROUP BY release_year ORDER BY release_year;
""", conn)
plt.figure(figsize=(10, 5))
sns.lineplot(data=q1, x="release_year", y="total_dramas", marker="o", linewidth=2.5)
plt.title("Korean Dramas Released by Year", fontsize=15, weight="bold")
plt.xlabel("Release Year")
plt.ylabel("Number of Dramas")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("outputs/dramas_by_year.png", dpi=300)
plt.show()
print("Interpretation: The chart shows how the number of popular Korean dramas "
      "changed over time. Higher counts in recent years suggest increased production.")

# Query 2: average rating per year
q2 = pd.read_sql_query("""
    SELECT strftime('%Y', first_air_date) AS release_year, ROUND(AVG(vote_average),2) AS average_rating
    FROM dramas GROUP BY release_year ORDER BY release_year;
""", conn)
plt.figure(figsize=(10, 5))
sns.lineplot(data=q2, x="release_year", y="average_rating", marker="o", linewidth=2.5)
plt.title("Average TMDB Rating by Release Year", fontsize=15, weight="bold")
plt.xlabel("Release Year")
plt.ylabel("Average Rating")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("outputs/average_rating_by_year.png", dpi=300)
plt.show()
print("Interpretation: Average ratings remain relatively stable across years. "
      "Earlier years contain far fewer dramas, so individual outliers have a much "
      "larger effect on the yearly average than recent years.")

# Query 3: top 10 highest-rated dramas (min 20 votes)
q3 = pd.read_sql_query("""
    SELECT name, vote_average, vote_count FROM dramas
    WHERE vote_count >= 20 ORDER BY vote_average DESC LIMIT 10;
""", conn)
plt.figure(figsize=(10, 6))
ax = sns.barplot(data=q3, x="vote_average", y="name")
plt.title("Top 10 Highest-Rated Korean Dramas", fontsize=15, weight="bold")
plt.xlabel("TMDB Rating")
plt.ylabel("")
for container in ax.containers:
    ax.bar_label(container, fmt="%.1f", padding=4)
plt.tight_layout()
plt.savefig("outputs/top_rated_dramas.png", dpi=300)
plt.show()
print("Interpretation: These dramas received the strongest audience ratings among "
      "popular Korean dramas with at least 20 votes, making the ranking more "
      "reliable by excluding shows with very few ratings.")

# Query 4: top 10 most popular dramas
q4 = pd.read_sql_query("""
    SELECT name, popularity FROM dramas ORDER BY popularity DESC LIMIT 10;
""", conn)
plt.figure(figsize=(10, 6))
ax = sns.barplot(data=q4, x="popularity", y="name")
plt.title("Top 10 Most Popular Korean Dramas", fontsize=15, weight="bold")
plt.xlabel("Popularity Score")
plt.ylabel("")
for container in ax.containers:
    ax.bar_label(container, fmt="%.0f", padding=4)
plt.tight_layout()
plt.savefig("outputs/top_popular_dramas.png", dpi=300)
plt.show()
print("Interpretation: Popularity scores highlight which dramas generated the "
      "greatest overall interest on TMDB.")

# Query 5: genre frequency
q5 = pd.read_sql_query("""
    SELECT 'Drama' AS genre, COUNT(*) AS total FROM dramas WHERE genre_names LIKE '%Drama%'
    UNION ALL SELECT 'Comedy', COUNT(*) FROM dramas WHERE genre_names LIKE '%Comedy%'
    UNION ALL SELECT 'Romance', COUNT(*) FROM dramas WHERE genre_names LIKE '%Romance%'
    UNION ALL SELECT 'Mystery', COUNT(*) FROM dramas WHERE genre_names LIKE '%Mystery%'
    UNION ALL SELECT 'Crime', COUNT(*) FROM dramas WHERE genre_names LIKE '%Crime%'
    UNION ALL SELECT 'Action & Adventure', COUNT(*) FROM dramas WHERE genre_names LIKE '%Action & Adventure%'
    ORDER BY total DESC;
""", conn)
plt.figure(figsize=(9, 5))
ax = sns.barplot(data=q5, x="genre", y="total")
plt.title("Most Common Genres in Popular Korean Dramas", fontsize=15, weight="bold")
plt.xlabel("")
plt.ylabel("Number of Dramas")
plt.xticks(rotation=30)
for container in ax.containers:
    ax.bar_label(container, padding=3)
plt.tight_layout()
plt.savefig("outputs/genre_frequency.png", dpi=300)
plt.show()
print("Interpretation: Drama appears most frequently, while genres like Crime and "
      "Mystery appear less often, showing that many popular Korean dramas combine "
      "drama with other genres. Note: TMDB's TV genre taxonomy does not include a "
      "standalone Romance category, so romance-themed dramas are typically "
      "classified under Drama instead — see README limitations.")

conn.close()