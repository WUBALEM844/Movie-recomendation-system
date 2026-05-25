# 🚀 Quick Start Guide

Get the recommendation system running in 5 minutes!

## 1. Install Python (if not already installed)

- Download from [python.org](https://www.python.org/)
- **Windows:** Use installer with "Add Python to PATH" checked
- **macOS:** Use Homebrew: `brew install python3`
- **Linux:** `sudo apt-get install python3 python3-pip`

## 2. Navigate to Project Directory

**Windows:**
```cmd
cd "C:\path\to\your\project"
```

**macOS/Linux:**
```bash
cd /path/to/your/project
```

## 3. Create Virtual Environment

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

> You should see `(venv)` at the start of your terminal line

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

> This takes ~2-3 minutes on first install

## 5. Get TMDB API Key (Optional but Recommended)

1. Visit [TMDB Settings](https://www.themoviedb.org/settings/api)
2. Create free account if needed
3. Request API key
4. Copy your key

## 6. Configure API Key

**Option A - Using .env file (Recommended):**

1. Open `.env` file in your project folder
2. Replace `your_api_key_here` with your API key
3. Save

**Option B - Skip (posters won't display):**
- Just run the app, it will work without posters

## 7. Run the Application

```bash
streamlit run streamlit_app.py
```

✅ **The app should open automatically in your browser!**

If it doesn't:
- Manually go to: `http://localhost:8501`

## 8. First Run

**On first run only:**
- App will download ~100MB MovieLens dataset
- Model will train (~30-60 seconds)
- This happens only once!

**Subsequent runs:**
- Instant launch (<5 seconds)

## 🎯 Try It Out

1. Keep default User ID (42) or pick another (1-943)
2. Click **"Generate Recommendations"** button
3. See 6 recommended movies with scores
4. Try filters: score, genre, search
5. View **Popular Movies** tab

## 📊 Test with Command Line

Before running Streamlit, test the core system:

```bash
python app.py
```

You should see:
```
Starting recommendation system pipeline...
Data loaded: 100000 ratings, 1682 movies
Building interaction matrix...
Training similarity model...
System ready for recommendations.

TOP RECOMMENDATIONS
=====================================
1. Movie Name
   Score: 0.8532
   Genres: Action, Adventure
...
```

## ❓ Common Issues

### "No module named streamlit"
```bash
pip install -r requirements.txt
```

### Port 8501 already in use
```bash
streamlit run streamlit_app.py --server.port 8502
```

### API key not working
- Verify key at [TMDB Settings](https://www.themoviedb.org/settings/api)
- Make sure it's in the `.env` file
- Restart the app after saving `.env`

### Dataset download fails
- Check internet connection
- Try again (sometimes network is temporary)
- Manually download from [MovieLens 100K](https://grouplens.org/datasets/movielens/100k/)

### Everything is slow
- First run: Normal (download + training)
- Second run: Should be instant
- If still slow: Check internet (API calls)

## 🎓 Next Steps

After getting it working:

1. **Try different users:** Change user ID to see different recommendations
2. **Test filters:** Use score, genre, and search filters
3. **Download CSV:** Export recommendations as file
4. **Check logs:** Run with `-v` flag for debugging: `python app.py`

## 📚 Learn More

- Full docs: See [README.md](README.md)
- Troubleshooting: See [README.md - Troubleshooting](README.md#troubleshooting)
- Algorithm details: See [README.md - How It Works](README.md#how-it-works)

## 🆘 Still Having Issues?

1. **Check terminal output** - error messages usually explain what's wrong
2. **Review README.md** - Full documentation with troubleshooting
3. **Verify Python installation:**
   ```bash
   python --version
   pip --version
   ```
4. **Try clean install:**
   ```bash
   pip uninstall -r requirements.txt
   pip install -r requirements.txt
   ```

---

**You're all set! Enjoy movie recommendations! 🍿🎬**
