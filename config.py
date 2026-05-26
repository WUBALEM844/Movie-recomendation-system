import os
from dotenv import load_dotenv

load_dotenv()

# Dataset Configurations
DATASET_URL = "https://github.com/lucasgatsas/book-crossing-dataset-minimal/raw/main/books_mini.zip"
DATASET_PATH = "book-dataset"

# Model Parameters
MODEL_NEIGHBORS = int(os.getenv("MODEL_NEIGHBORS", "10"))
MIN_RATING_COUNT = int(os.getenv("MIN_BOOK_RATING_COUNT", "5"))