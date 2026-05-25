# 🎬 AI Movie Recommendation System

A Netflix-style movie recommendation system using collaborative filtering and the MovieLens 100K dataset with movie posters from TMDB.

## Features

✨ **Key Features:**
- 🤖 **Item-Based Collaborative Filtering** - Recommends movies based on user preferences
- 🎭 **Genre Filtering** - Filter recommendations by genre
- 🔍 **Movie Search** - Search for specific movies
- ⭐ **Score-based Filtering** - Filter by prediction confidence
- 📷 **Movie Posters** - Display posters from TMDB API
- 📊 **Popular Movies Tab** - View most popular movies in dataset
- 💾 **Export Recommendations** - Download recommendations as CSV
- 📱 **Responsive UI** - Built with Streamlit for easy interaction

## Prerequisites

- Python 3.8+
- pip (Python package manager)

## Installation

### 1. Clone/Setup the Project

```bash
cd "path/to/your/project"
```

### 2. Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Key

#### Get TMDB API Key:
1. Go to [TMDB API Settings](https://www.themoviedb.org/settings/api)
2. Create a free account if you don't have one
3. Request an API key (Movie Database API)
4. Copy your API key

#### Set Environment Variable:

**Option A: Using .env file (Recommended)**

1. Open `.env` file in your project
2. Replace `your_api_key_here` with your actual TMDB API key
3. Save the file

```env
TMDB_API_KEY=your_actual_api_key_here
```

**Option B: Using System Environment Variable**

**Windows (PowerShell):**
```powershell
$env:TMDB_API_KEY = "your_api_key_here"
```

**Windows (Command Prompt):**
```cmd
set TMDB_API_KEY=your_api_key_here
```

**macOS/Linux (Bash):**
```bash
export TMDB_API_KEY=your_api_key_here
```

## Usage

### Run the Application

```bash
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

### How to Use

#### Tab 1: Get Recommendations

1. **Select User ID** - Choose a user (1-943) to get personalized recommendations
2. **Configure Filters:**
   - Set number of recommendations (1-12)
   - Set minimum score threshold
   - Filter by genre (optional)
   - Search for specific movies (optional)
3. **Generate** - Click the "Generate Recommendations" button
4. **View & Export** - Browse recommendations and download as CSV

#### Tab 2: Popular Movies

1. Select how many popular movies to display
2. Click "Load Popular Movies"
3. View the most frequently rated movies in the dataset

## Testing

### Test with Command Line

```bash
python app.py
```

This will:
1. Download the MovieLens 100K dataset (if not present)
2. Load and preprocess the data
3. Train the recommendation model
4. Generate sample recommendations for user 42

### Expected Output

```
Starting recommendation system pipeline...
Downloading dataset...
Dataset downloaded successfully.
Data loaded: 100000 ratings, 1682 movies
Building interaction matrix...
Matrix prepared successfully.
Training similarity model...
Model trained successfully.
System ready for recommendations.

TOP RECOMMENDATIONS
========================================
1. Movie Title 1
   Score: 0.8532
   Genres: Action, Adventure
2. Movie Title 2
   Score: 0.7891
   Genres: Drama, Romance
...
```

## Project Structure

```
├── app.py                  # Core recommendation engine
├── streamlit_app.py        # Streamlit UI
├── config.py              # Configuration & constants
├── requirements.txt       # Python dependencies
├── .env                   # API key configuration (local, not in git)
├── .env.example          # Example configuration template
├── ml-100k/              # Dataset directory (auto-downloaded)
│   ├── u.data           # User ratings
│   ├── u.item           # Movie information
│   ├── u.genre          # Genre mappings
│   └── ...
└── README.md             # This file
```

## Configuration

### config.py Options

You can customize behavior by editing `.env`:

```env
# API Configuration
TMDB_API_KEY=your_api_key_here

# Dataset path (default: ml-100k)
DATASET_PATH=ml-100k

# Model parameters (default: 20)
MODEL_NEIGHBORS=20

# Minimum rating count for movies (default: 5)
MIN_RATING_COUNT=5
```

## Data

### MovieLens 100K Dataset

- **Source:** [MovieLens 100K](https://grouplens.org/datasets/movielens/100k/)
- **Size:** ~100,000 ratings from 943 users on 1,682 movies
- **Rating Scale:** 1-5 stars
- **Genres:** 19 different genres

### TMDB Movie Posters

- **Source:** [The Movie Database (TMDB)](https://www.themoviedb.org/)
- **API:** Free API with account registration
- **Usage:** Poster images for enhanced UI

## How It Works

### Algorithm: Item-Based Collaborative Filtering

1. **Build Interaction Matrix** - Create user-item rating matrix
2. **Normalize** - Remove user bias by mean-centering ratings
3. **Train Model** - Use K-NN with cosine similarity to find similar movies
4. **Recommend** - For watched movies, find similar unwatched movies with high scores

### Recommendation Steps

1. Get user's watched movies
2. Find similar movies using K-NN (cosine similarity)
3. Score recommendations based on similarity
4. Aggregate scores and rank
5. Return top-N movies

## Troubleshooting

### Issue: "TMDB_API_KEY not set"

**Solution:** 
- Check if `.env` file exists and has correct API key
- Verify API key is valid at [TMDB Settings](https://www.themoviedb.org/settings/api)
- Make sure `python-dotenv` is installed: `pip install python-dotenv`

### Issue: "Dataset download failed"

**Solution:**
- Check internet connection
- Verify the download URL is accessible
- Try manually downloading from [MovieLens](https://grouplens.org/datasets/movielens/100k/)
- Extract to `ml-100k/` folder in project directory

### Issue: "ModuleNotFoundError"

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: Streamlit not launching

**Solution:**
```bash
pip install --upgrade streamlit
streamlit run streamlit_app.py
```

### Issue: No poster images showing

**Solution:**
- Verify TMDB API key is valid
- Check internet connection (API requires live requests)
- Posters will work on app reload after setting API key

## Performance Tips

- First run: ~1-2 minutes (dataset download + model training)
- Subsequent runs: <30 seconds (cached model)
- API calls: ~0.5 seconds per poster load
- Large top_n values: May take longer due to more API calls

## Security Notes

⚠️ **Important:**
- Never commit `.env` file to version control
- Never share your TMDB API key
- Use `.env.example` as template
- For production: Use environment variables or secrets manager

## Dependencies

| Package | Purpose |
|---------|---------|
| streamlit | Web UI framework |
| numpy | Numerical computing |
| pandas | Data manipulation |
| scikit-learn | Machine learning (K-NN) |
| requests | HTTP requests (TMDB API) |
| python-dotenv | Environment variable management |

## Future Improvements

- 🔐 User authentication
- 📈 Rating prediction (regression)
- 🎯 Hybrid recommendations (content + collaborative)
- 📊 Recommendation explanations
- 💾 Save favorite recommendations
- 🌐 Multi-language support
- ⚡ Performance optimization for large datasets

## Credits

- **Dataset:** [GroupLens](https://grouplens.org/) - MovieLens 100K
- **Posters API:** [TMDB](https://www.themoviedb.org/) - The Movie Database
- **Algorithm:** Item-Based Collaborative Filtering with K-Nearest Neighbors

## License

This project is for educational purposes.

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review error messages in the terminal
3. Verify configuration in `.env`
4. Check dependencies: `pip list`

---

**Happy movie watching! 🍿🎬**
