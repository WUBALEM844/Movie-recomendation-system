import os
import logging
import zipfile
import urllib.request
from typing import List, Dict, Any

import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from config import DATASET_URL, DATASET_PATH, MODEL_NEIGHBORS, MIN_RATING_COUNT

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BookRecommender:
    def __init__(self):
        self.ratings_df = None
        self.books_df = None
        self.interaction_matrix = None
        self.normalized_matrix = None
        self.model = None

    def download_dataset(self):
        if os.path.exists(DATASET_PATH):
            return
        try:
            logger.info("Downloading book dataset...")
            zip_path = "books_mini.zip"
            urllib.request.urlretrieve(DATASET_URL, zip_path)
            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(DATASET_PATH)
            os.remove(zip_path)
            logger.info("Book dataset downloaded and ready.")
        except Exception as e:
            logger.error(f"Error downloading data: {e}")
            self.create_mock_data()

    def create_mock_data(self):
        logger.info("Creating optimized fallback dataset...")
        os.makedirs(DATASET_PATH, exist_ok=True)
        np.random.seed(42)
        mock_ratings = pd.DataFrame({
            "User-ID": np.random.randint(1001, 1050, size=500, dtype=np.int32),
            "ISBN": np.random.randint(2001, 2030, size=500, dtype=np.int32),
            "Book-Rating": np.random.randint(1, 11, size=500, dtype=np.int8)
        })
        mock_ratings.to_csv(f"{DATASET_PATH}/Ratings.csv", index=False)

        titles = ["The Great Gatsby", "1984", "The Hobbit", "Harry Potter", "Sapiens", "Educated"]
        books_list = [{"ISBN": i, "Book-Title": f"{titles[i % len(titles)]} Vol {i-2000}", "Book-Author": f"Author {i}"} for i in range(2001, 2031)]
        pd.DataFrame(books_list).to_csv(f"{DATASET_PATH}/Books.csv", index=False)

    def load_and_minimize_data(self):
        try:
            self.ratings_df = pd.read_csv(f"{DATASET_PATH}/Ratings.csv", dtype={"User-ID": np.int32, "ISBN": np.int32, "Book-Rating": np.int8})
            self.books_df = pd.read_csv(f"{DATASET_PATH}/Books.csv", dtype={"ISBN": np.int32})

            # Data Minimization
            book_counts = self.ratings_df["ISBN"].value_counts()
            popular_books = book_counts[book_counts >= MIN_RATING_COUNT].index
            self.ratings_df = self.ratings_df[self.ratings_df["ISBN"].isin(popular_books)].reset_index(drop=True)
            self.books_df = self.books_df[self.books_df["ISBN"].isin(popular_books)].reset_index(drop=True)
            logger.info("Dataset loading and minimization complete.")
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self.create_mock_data()
            self.load_and_minimize_data()

    def prepare_matrices(self):
        self.interaction_matrix = self.ratings_df.pivot_table(index="User-ID", columns="ISBN", values="Book-Rating").astype(np.float32)
        user_means = self.interaction_matrix.mean(axis=1)
        self.normalized_matrix = self.interaction_matrix.sub(user_means, axis=0).fillna(0).astype(np.float32)

    def train(self):
        self.model = NearestNeighbors(metric="cosine", algorithm="brute", n_neighbors=MODEL_NEIGHBORS)
        self.model.fit(self.normalized_matrix.T)
        logger.info("Model training complete.")

    def get_book_cover(self, isbn: int) -> str:
        return f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg"

    def recommend_books(self, user_id: int, top_n: int = 5) -> List[Dict[str, Any]]:
        if user_id not in self.interaction_matrix.index:
            return self.get_popular_books(top_n)

        user_ratings = self.interaction_matrix.loc[user_id]
        read_books = user_ratings.dropna().index.tolist()
        scores = {}
        isbn_map = {isbn: idx for idx, isbn in enumerate(self.normalized_matrix.columns)}

        for isbn in read_books:
            if isbn not in isbn_map: continue
            idx = isbn_map[isbn]
            distances, indices = self.model.kneighbors([self.normalized_matrix.T.iloc[idx]], n_neighbors=min(MODEL_NEIGHBORS, len(isbn_map)))
            for i in range(1, len(indices.flatten())):
                sim_idx = indices.flatten()[i]
                sim_isbn = self.normalized_matrix.columns[sim_idx]
                if sim_isbn in read_books: continue
                score = 1.0 - distances.flatten()[i]
                scores[sim_isbn] = scores.get(sim_isbn, 0.0) + score

        if not scores: return self.get_popular_books(top_n)
        sorted_isbns = pd.Series(scores).sort_values(ascending=False).head(top_n)
        
        results = []
        for isbn, score in sorted_isbns.items():
            row = self.books_df[self.books_df["ISBN"] == isbn]
            if row.empty: continue
            results.append({
                "isbn": int(isbn),
                "title": row["Book-Title"].values[0],
                "author": row["Book-Author"].values[0] if "Book-Author" in row.columns else "Unknown",
                "score": round(float(score), 4),
                "cover": self.get_book_cover(isbn)
            })
        return results

    def get_popular_books(self, top_n=5):
        top_isbns = self.ratings_df["ISBN"].value_counts().head(top_n).index
        results = []
        for isbn in top_isbns:
            row = self.books_df[self.books_df["ISBN"] == isbn]
            if row.empty: continue
            results.append({
                "isbn": int(isbn),
                "title": row["Book-Title"].values[0],
                "author": row["Book-Author"].values[0] if "Book-Author" in row.columns else "Unknown",
                "score": 0.0,
                "cover": self.get_book_cover(isbn)
            })
        return results

    def run_pipeline(self):
        self.download_dataset()
        self.load_and_minimize_data()
        self.prepare_matrices()
        self.train()

if __name__ == "__main__":
    recommender = BookRecommender()
    recommender.run_pipeline()
    sample_user = recommender.ratings_df["User-ID"].iloc[0]
    print(f"\nRecommendations for User {sample_user}:")
    print(recommender.recommend_books(user_id=int(sample_user), top_n=3))