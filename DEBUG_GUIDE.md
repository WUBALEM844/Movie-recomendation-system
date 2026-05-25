# 🔧 Debugging Guide

Comprehensive guide to diagnose and fix common issues.

## 1. Verify Installation

### Check Python
```bash
python --version
```
Should show: `Python 3.8.x` or higher

### Check pip
```bash
pip --version
```
Should show: `pip 20.x` or higher

### List Installed Packages
```bash
pip list
```
Should include:
- streamlit ✓
- numpy ✓
- pandas ✓
- scikit-learn ✓
- requests ✓
- python-dotenv ✓

**If missing:** Run `pip install -r requirements.txt`

## 2. Test Core App

### Basic Test
```bash
python app.py
```

**Expected flow:**
1. Download dataset (if needed) - ~100MB
2. Load data
3. Build matrix
4. Train model
5. Print recommendations

**If fails:** Check error message in console

### Test Specific Components

**Test imports:**
```python
python -c "import streamlit; import numpy; import pandas; import sklearn; import requests; print('All imports OK')"
```

**Test config:**
```python
python -c "from config import API_KEY, DISPLAY_GENRES, validate_config; print(f'Config valid: {validate_config()[0]}')"
```

**Test API key:**
```python
python -c "from config import API_KEY; print(f'API Key set: {bool(API_KEY)}')"
```

## 3. Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'streamlit'"

**Cause:** Streamlit not installed or wrong environment

**Solution:**
```bash
# Make sure virtual environment is activated
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Reinstall
pip install -r requirements.txt
```

### Issue: "ModuleNotFoundError: No module named 'config'"

**Cause:** Working directory is not the project folder

**Solution:**
```bash
# Make sure you're in the right directory
cd "path/to/your/project"
python app.py
```

### Issue: "TMDB_API_KEY not configured"

**Cause:** API key not set or .env file not found

**Solution:**
```bash
# Check if .env file exists
# Windows:
dir .env
# macOS/Linux:
ls -la .env

# If not found, create it:
# Copy .env.example to .env and add your key
# Or set environment variable:
# Windows:
set TMDB_API_KEY=your_key_here
# macOS/Linux:
export TMDB_API_KEY=your_key_here
```

**Verify API key:**
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(f'API Key: {os.getenv(\"TMDB_API_KEY\")}')"
```

### Issue: "Dataset download failed"

**Cause:** Network error or URL issue

**Solution:**
```bash
# Check internet connection
ping google.com

# Delete old download and retry
# Windows:
del ml-100k.zip
python app.py

# macOS/Linux:
rm ml-100k.zip
python app.py

# Or manually download:
# Visit: https://grouplens.org/datasets/movielens/100k/
# Extract to ml-100k/ folder
```

### Issue: Streamlit port already in use

**Cause:** Another instance running or port conflict

**Solution:**
```bash
# Use different port
streamlit run streamlit_app.py --server.port 8502

# Or kill existing process
# Windows (PowerShell):
Get-Process python | Stop-Process -Force

# macOS/Linux:
killall python
```

### Issue: Model training takes very long

**Cause:** Large dataset or slow computer

**Expected times:**
- First run: 1-2 minutes
- Model cached: <5 seconds
- API calls: ~0.5-1 second per movie

**Solution:**
- Be patient on first run
- Reduce MODEL_NEIGHBORS in .env (default: 20)
- Close other applications

### Issue: No poster images

**Cause:** API key not valid or API error

**Solution:**
```bash
# Verify API key is valid
python -c "
import requests
from config import API_KEY
url = 'https://api.themoviedb.org/3/search/movie'
params = {'api_key': API_KEY, 'query': 'Avatar'}
try:
    r = requests.get(url, params=params, timeout=5).json()
    print(f'API Status: {\"OK\" if r.get(\"results\") else \"No results\"}')
except Exception as e:
    print(f'API Error: {e}')
"

# Get new key from https://www.themoviedb.org/settings/api
# Update .env file
# Restart app
```

### Issue: Recommendations all show score 0

**Cause:** User not found or matrix issue

**Solution:**
```bash
# Check valid user range
python -c "
from app import AdvancedMovieRecommender
m = AdvancedMovieRecommender()
m.download_dataset()
m.load_data()
m.prepare_data()
print(f'Valid users: 1 to {m.interaction_matrix.index.max()}')
"

# Try user 1-100 range first
```

### Issue: Streamlit won't start

**Cause:** Various startup issues

**Solution:**
```bash
# Clear Streamlit cache
# Windows:
rmdir /s %USERPROFILE%\.streamlit
# macOS/Linux:
rm -rf ~/.streamlit

# Update Streamlit
pip install --upgrade streamlit

# Try with verbose output
streamlit run streamlit_app.py --logger.level=debug
```

## 4. Enable Debug Logging

### Run app with debug logging

```bash
# Python script
PYTHONUNBUFFERED=1 python app.py

# Streamlit
streamlit run streamlit_app.py --logger.level=debug
```

### View Streamlit logs

```bash
# macOS/Linux
tail -f ~/.streamlit/logs/

# Windows (PowerShell)
Get-Content $env:USERPROFILE\.streamlit\logs\* -Wait
```

## 5. Performance Debugging

### Check what's slow

```python
import time
from app import AdvancedMovieRecommender

model = AdvancedMovieRecommender()

# Time each step
start = time.time()
model.download_dataset()
print(f"Download: {time.time() - start:.2f}s")

start = time.time()
model.load_data()
print(f"Load data: {time.time() - start:.2f}s")

start = time.time()
model.prepare_data()
print(f"Prepare: {time.time() - start:.2f}s")

start = time.time()
model.train_model()
print(f"Train: {time.time() - start:.2f}s")

start = time.time()
recs = model.recommend_movies(42, 10)
print(f"Recommend: {time.time() - start:.2f}s")
```

## 6. Data Debugging

### Verify dataset

```python
from app import AdvancedMovieRecommender
import pandas as pd

model = AdvancedMovieRecommender()
model.download_dataset()
model.load_data()

print(f"Ratings: {len(model.ratings_df)}")
print(f"Movies: {len(model.movies_df)}")
print(f"Users: {model.ratings_df['user_id'].nunique()}")
print(f"Rating range: {model.ratings_df['rating'].min()} - {model.ratings_df['rating'].max()}")

# Show sample data
print("\nSample ratings:")
print(model.ratings_df.head())

print("\nSample movies:")
print(model.movies_df[['item_id', 'movie_title']].head())
```

### Check genres

```python
from config import GENRES, DISPLAY_GENRES
print("All genres:", GENRES)
print("Display genres:", DISPLAY_GENRES)
```

## 7. API Debugging

### Test TMDB API

```python
import requests
from config import API_KEY

print(f"API Key: {API_KEY[:10]}..." if API_KEY else "No API Key")

if API_KEY:
    url = "https://api.themoviedb.org/3/search/movie"
    params = {"api_key": API_KEY, "query": "Avatar"}
    
    response = requests.get(url, params=params, timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Results: {len(response.json().get('results', []))}")
    
    if response.json().get('results'):
        movie = response.json()['results'][0]
        poster = movie.get('poster_path')
        print(f"Poster: {'Yes' if poster else 'No'}")
```

## 8. Streamlit Debugging

### Check session state

Add to `streamlit_app.py`:
```python
st.write("Debug Info:")
st.write(st.session_state)
```

### Clear cache

```bash
streamlit cache clear
```

## 9. System Information

Gather info for troubleshooting:

```bash
# Windows (PowerShell)
python --version
pip --version
pip list
echo $env:TMDB_API_KEY
Get-Location

# macOS/Linux (Bash)
python3 --version
pip3 --version
pip3 list
echo $TMDB_API_KEY
pwd
```

## 10. Getting Help

When reporting issues, include:

1. **System info:**
   ```bash
   python --version
   pip list
   ```

2. **Error output:**
   - Full error message from terminal
   - Last 10-20 lines of output

3. **What you tried:**
   - Commands you ran
   - Changes you made

4. **Environment:**
   - Windows/macOS/Linux version
   - Virtual environment active?
   - .env file configured?

---

**Still stuck? Review README.md or try fresh install!**
