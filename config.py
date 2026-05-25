import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# TMDB API Key (get from environment variable)
API_KEY = os.getenv("TMDB_API_KEY", "")

# Dataset configuration
DATASET_PATH = os.getenv("DATASET_PATH", "ml-100k")
DATASET_URL = "https://files.grouplens.org/datasets/movielens/ml-100k.zip"

# Model parameters
MODEL_NEIGHBORS = int(os.getenv("MODEL_NEIGHBORS", "20"))
MIN_RATING_COUNT = int(os.getenv("MIN_RATING_COUNT", "5"))

# Genres list (complete from dataset)
GENRES = [
    "unknown", "Action", "Adventure", "Animation", "Children",
    "Comedy", "Crime", "Documentary", "Drama", "Fantasy",
    "Film-Noir", "Horror", "Musical", "Mystery", "Romance",
    "Sci-Fi", "Thriller", "War", "Western"
]

# UI Configuration
DISPLAY_GENRES = [
    "Action", "Adventure", "Animation", "Children",
    "Comedy", "Crime", "Documentary", "Drama",
    "Fantasy", "Horror", "Romance", "Sci-Fi", "Thriller", "War"
]

# Validation
if not API_KEY:
    print("⚠️  WARNING: TMDB_API_KEY not set. Posters will not load. Set it in .env file or environment variable.")

def validate_config():
    """Validate that all required configuration is set"""
    if not API_KEY:
        return False, "TMDB_API_KEY is required"
    return True, "Configuration valid"