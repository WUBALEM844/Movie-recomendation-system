import os
import logging
import zipfile
import urllib.request
from typing import List, Dict, Any

import numpy as np
import pandas as pd
import requests

from sklearn.neighbors import NearestNeighbors
from config import API_KEY, DATASET_PATH, GENRES, DISPLAY_GENRES, MODEL_NEIGHBORS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AdvancedMovieRecommender:
    """
    Professional Movie Recommendation System
    (Item-Based Collaborative Filtering + TMDB Posters)
    """

    DATASET_URL = "https://files.grouplens.org/datasets/movielens/ml-100k.zip"

    def __init__(self):
        self.ratings_df = None
        self.movies_df = None

        self.interaction_matrix = None
        self.normalized_matrix = None

        self.movie_similarity_model = None
        self.dataset_path = DATASET_PATH

    # =========================
    # TMDB POSTER API
    # =========================
    def get_poster(self, title: str):
        """Fetch movie poster from TMDB API"""
        if not API_KEY:
            logger.warning(f"API key not configured. Cannot fetch poster for {title}")
            return None

        url = "https://api.themoviedb.org/3/search/movie"

        params = {
            "api_key": API_KEY,
            "query": title
        }

        try:
            res = requests.get(url, params=params, timeout=5).json()

            if res.get("results"):
                poster = res["results"][0].get("poster_path")
                if poster:
                    return "https://image.tmdb.org/t/p/w500" + poster

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching poster for {title}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching poster: {e}")

        return None

    # =========================
    # DOWNLOAD DATASET
    # =========================
    def download_dataset(self):
        """Download and extract MovieLens dataset"""
        if os.path.exists(self.dataset_path):
            logger.info("Dataset already exists. Skipping download.")
            return

        try:
            logger.info("Downloading dataset...")

            zip_path = "ml-100k.zip"

            urllib.request.urlretrieve(self.DATASET_URL, zip_path)

            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(".")

            os.remove(zip_path)

            logger.info("Dataset downloaded successfully.")
        except Exception as e:
            logger.error(f"Error downloading dataset: {e}")
            raise

    # =========================
    # LOAD DATA
    # =========================
    def load_data(self):
        """Load ratings and movie data"""
        try:
            ratings_cols = ["user_id", "item_id", "rating", "timestamp"]

            self.ratings_df = pd.read_csv(
                f"{self.dataset_path}/u.data",
                sep="\t",
                names=ratings_cols,
                encoding="latin-1"
            )

            movie_cols = [
                "item_id", "movie_title", "release_date", "video_release_date",
                "IMDb_URL"
            ] + GENRES

            self.movies_df = pd.read_csv(
                f"{self.dataset_path}/u.item",
                sep="|",
                names=movie_cols,
                encoding="latin-1"
            )

            logger.info(f"Data loaded: {len(self.ratings_df)} ratings, {len(self.movies_df)} movies")
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise

    # =========================
    # PREPROCESS
    # =========================
    def prepare_data(self):
        """Build and normalize interaction matrix"""
        try:
            logger.info("Building interaction matrix...")

            self.interaction_matrix = self.ratings_df.pivot_table(
                index="user_id",
                columns="item_id",
                values="rating"
            )

            user_means = self.interaction_matrix.mean(axis=1)

            self.normalized_matrix = self.interaction_matrix.sub(
                user_means, axis=0
            ).fillna(0)

            logger.info("Matrix prepared successfully.")
        except Exception as e:
            logger.error(f"Error preparing data: {e}")
            raise

    # =========================
    # TRAIN MODEL
    # =========================
    def train_model(self):
        """Train K-NN similarity model"""
        try:
            logger.info("Training similarity model...")

            self.movie_similarity_model = NearestNeighbors(
                metric="cosine",
                algorithm="brute",
                n_neighbors=MODEL_NEIGHBORS
            )

            self.movie_similarity_model.fit(self.normalized_matrix.T)

            logger.info("Model trained successfully.")
        except Exception as e:
            logger.error(f"Error training model: {e}")
            raise

    # =========================
    # POPULAR MOVIES
    # =========================
    def get_popular_movies(self, top_n=10):
        """Get most popular movies from dataset"""
        try:
            top = self.ratings_df["item_id"].value_counts().head(top_n)

            results = []

            for item_id in top.index:

                row = self.movies_df[self.movies_df["item_id"] == item_id]

                if row.empty:
                    continue

                title = row["movie_title"].values[0]

                genres = [
                    g for g in DISPLAY_GENRES
                    if g in self.movies_df.columns and row[g].values[0] == 1
                ]

                results.append({
                    "movie_id": int(item_id),
                    "title": title,
                    "predicted_score": 0,
                    "genres": genres,
                    "poster": self.get_poster(title)
                })

            return results
        except Exception as e:
            logger.error(f"Error getting popular movies: {e}")
            return []

    # =========================
    # RECOMMENDATION ENGINE
    # =========================
    def recommend_movies(self, user_id: int, top_n: int = 5):
        """Generate movie recommendations for a user"""
        try:
            if user_id not in self.interaction_matrix.index:
                logger.info(f"User {user_id} not found. Returning popular movies.")
                return self.get_popular_movies(top_n)

            user_ratings = self.interaction_matrix.loc[user_id]
            watched = user_ratings.dropna().index.tolist()

            scores = {}

            item_index_map = {
                item: idx for idx, item in enumerate(self.normalized_matrix.columns)
            }

            for movie_id in watched:

                if movie_id not in item_index_map:
                    continue

                idx = item_index_map[movie_id]

                distances, indices = self.movie_similarity_model.kneighbors(
                    [self.normalized_matrix.T.iloc[idx]],
                    n_neighbors=10
                )

                for i in range(1, len(indices.flatten())):

                    sim_idx = indices.flatten()[i]
                    sim_movie = self.normalized_matrix.columns[sim_idx]

                    if sim_movie in watched:
                        continue

                    score = 1 - distances.flatten()[i]
                    scores[sim_movie] = scores.get(sim_movie, 0) + score

            scores = pd.Series(scores).sort_values(ascending=False).head(top_n)

            results = []

            for item_id, score in scores.items():

                row = self.movies_df[self.movies_df["item_id"] == item_id]

                if row.empty:
                    continue

                title = row["movie_title"].values[0]

                genres = [
                    g for g in DISPLAY_GENRES
                    if g in self.movies_df.columns and row[g].values[0] == 1
                ]

                results.append({
                    "movie_id": int(item_id),
                    "title": title,
                    "predicted_score": round(float(score), 4),
                    "genres": genres,
                    "poster": self.get_poster(title)
                })

            logger.info(f"Generated {len(results)} recommendations for user {user_id}")
            return results
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return self.get_popular_movies(top_n)

    # =========================
    # PIPELINE
    # =========================
    def run_pipeline(self):
        """Execute the full recommendation pipeline"""
        try:
            logger.info("Starting recommendation system pipeline...")

            self.download_dataset()
            self.load_data()
            self.prepare_data()
            self.train_model()

            logger.info("System ready for recommendations.")
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            raise


# =========================
# TEST RUN
# =========================
if __name__ == "__main__":

    model = AdvancedMovieRecommender()

    model.run_pipeline()

    recs = model.recommend_movies(user_id=42)

    print("\nTOP RECOMMENDATIONS\n" + "=" * 40)

    for i, m in enumerate(recs, 1):
        print(f"{i}. {m['title']}")
        print(f"   Score: {m['predicted_score']}")
        print(f"   Genres: {m['genres']}")


class AdvancedMovieRecommender:
    """
    Professional Movie Recommendation System
    (Item-Based Collaborative Filtering + TMDB Posters)
    """

    DATASET_URL = "https://files.grouplens.org/datasets/movielens/ml-100k.zip"

    def __init__(self):
        self.ratings_df = None
        self.movies_df = None

        self.interaction_matrix = None
        self.normalized_matrix = None

        self.movie_similarity_model = None

    # =========================
    # TMDB POSTER API
    # =========================
    def get_poster(self, title: str):

        url = "https://api.themoviedb.org/3/search/movie"

        params = {
            "api_key": API_KEY,
            "query": title
        }

        try:
            res = requests.get(url, params=params, timeout=5).json()

            if res.get("results"):
                poster = res["results"][0].get("poster_path")
                if poster:
                    return "https://image.tmdb.org/t/p/w500" + poster

        except Exception:
            pass

        return None

    # =========================
    # DOWNLOAD DATASET
    # =========================
    def download_dataset(self):

        if not os.path.exists("ml-100k"):

            print("Downloading dataset...")

            zip_path = "ml-100k.zip"

            urllib.request.urlretrieve(self.DATASET_URL, zip_path)

            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(".")

            os.remove(zip_path)

            print("Dataset downloaded.")

    # =========================
    # LOAD DATA
    # =========================
    def load_data(self):

        ratings_cols = ["user_id", "item_id", "rating", "timestamp"]

        self.ratings_df = pd.read_csv(
            "ml-100k/u.data",
            sep="\t",
            names=ratings_cols,
            encoding="latin-1"
        )

        movie_cols = [
            "item_id", "movie_title", "release_date", "video_release_date",
            "IMDb_URL", "unknown", "Action", "Adventure", "Animation",
            "Children", "Comedy", "Crime", "Documentary", "Drama",
            "Fantasy", "Film-Noir", "Horror", "Musical", "Mystery",
            "Romance", "Sci-Fi", "Thriller", "War", "Western"
        ]

        self.movies_df = pd.read_csv(
            "ml-100k/u.item",
            sep="|",
            names=movie_cols,
            encoding="latin-1"
        )

        print("Data loaded successfully.")

    # =========================
    # PREPROCESS
    # =========================
    def prepare_data(self):

        print("Building interaction matrix...")

        self.interaction_matrix = self.ratings_df.pivot_table(
            index="user_id",
            columns="item_id",
            values="rating"
        )

        user_means = self.interaction_matrix.mean(axis=1)

        self.normalized_matrix = self.interaction_matrix.sub(
            user_means, axis=0
        ).fillna(0)

        print("Matrix ready.")

    # =========================
    # TRAIN MODEL
    # =========================
    def train_model(self):

        print("Training similarity model...")

        self.movie_similarity_model = NearestNeighbors(
            metric="cosine",
            algorithm="brute",
            n_neighbors=20
        )

        self.movie_similarity_model.fit(self.normalized_matrix.T)

        print("Model trained.")

    # =========================
    # POPULAR MOVIES
    # =========================
    def get_popular_movies(self, top_n=10):

        top = self.ratings_df["item_id"].value_counts().head(top_n)

        results = []

        for item_id in top.index:

            row = self.movies_df[self.movies_df["item_id"] == item_id]

            if row.empty:
                continue

            title = row["movie_title"].values[0]

            results.append({
                "movie_id": int(item_id),
                "title": title,
                "predicted_score": 0,
                "genres": [],
                "poster": self.get_poster(title)
            })

        return results

    # =========================
    # RECOMMENDATION ENGINE
    # =========================
    def recommend_movies(self, user_id: int, top_n: int = 5):

        if user_id not in self.interaction_matrix.index:
            return self.get_popular_movies(top_n)

        user_ratings = self.interaction_matrix.loc[user_id]
        watched = user_ratings.dropna().index.tolist()

        scores = {}

        item_index_map = {
            item: idx for idx, item in enumerate(self.normalized_matrix.columns)
        }

        for movie_id in watched:

            if movie_id not in item_index_map:
                continue

            idx = item_index_map[movie_id]

            distances, indices = self.movie_similarity_model.kneighbors(
                [self.normalized_matrix.T.iloc[idx]],
                n_neighbors=10
            )

            for i in range(1, len(indices.flatten())):

                sim_idx = indices.flatten()[i]
                sim_movie = self.normalized_matrix.columns[sim_idx]

                if sim_movie in watched:
                    continue

                score = 1 - distances.flatten()[i]
                scores[sim_movie] = scores.get(sim_movie, 0) + score

        scores = pd.Series(scores).sort_values(ascending=False).head(top_n)

        results = []

        for item_id, score in scores.items():

            row = self.movies_df[self.movies_df["item_id"] == item_id]

            if row.empty:
                continue

            title = row["movie_title"].values[0]

            genres = [
                g for g in [
                    "Action", "Adventure", "Animation", "Children",
                    "Comedy", "Crime", "Documentary", "Drama",
                    "Fantasy", "Horror", "Romance", "Sci-Fi"
                ] if row[g].values[0] == 1
            ]

            results.append({
                "movie_id": int(item_id),
                "title": title,
                "predicted_score": round(float(score), 4),
                "genres": genres,
                "poster": self.get_poster(title)
            })

        return results

    # =========================
    # PIPELINE
    # =========================
    def run_pipeline(self):

        self.download_dataset()
        self.load_data()
        self.prepare_data()
        self.train_model()

        print("System ready.")


# =========================
# TEST RUN
# =========================
if __name__ == "__main__":

    model = AdvancedMovieRecommender()

    model.run_pipeline()

    recs = model.recommend_movies(user_id=42)

    print("\nTOP RECOMMENDATIONS\n" + "=" * 40)

    for i, m in enumerate(recs, 1):
        print(f"{i}. {m['title']}")
        print(f"   Score: {m['predicted_score']}")
        print(f"   Genres: {m['genres']}")