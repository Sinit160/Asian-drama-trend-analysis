import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity
import scipy.sparse as sp

'''Here I build a content-based recommender using one-hot encoded genres
and TF-IDF vectorized overviews, combined into one feature matrix and
compared using cosine similarity.'''

df = pd.read_csv('data/cleaned_dramas.csv')

df["genre_list"] = df["genre_names"].apply(lambda x: x.split(", "))
df["overview"] = df["overview"].fillna("No overview available")

mlb = MultiLabelBinarizer()
genre_matrix = mlb.fit_transform(df["genre_list"])

tfidf = TfidfVectorizer(stop_words="english")
overview_matrix = tfidf.fit_transform(df["overview"])

combined_features = sp.hstack([overview_matrix, genre_matrix])
similarity_matrix = cosine_similarity(combined_features)


def recommend_dramas(title, n=5):
    if title not in df["name"].values:
        return f"'{title}' not found."

    index = df[df["name"] == title].index[0]
    scores = list(enumerate(similarity_matrix[index]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    top_scores = scores[1:n + 1]

    recommendations = pd.DataFrame({
        "Recommended Show": [df.iloc[i]["name"] for i, _ in top_scores],
        "Similarity Score": [round(score, 3) for _, score in top_scores]
    })
    return recommendations


if __name__ == "__main__":
    print("\n=== Korean Drama Recommender ===")
    print('Enter a drama title to get recommendations.')
    print('Type "done" to exit.\n')
    while True:
        user_choice = input("Enter a drama title: ").strip()
        if user_choice.lower() == "done":
            print("Thanks for using the Korean Drama Recommender!")
            break
        print("\nRecommendations:")
        print(recommend_dramas(user_choice))
        print()