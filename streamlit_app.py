import streamlit as st
from app import AdvancedMovieRecommender

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="AI Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# -------------------------
# LOAD MODEL
# -------------------------
@st.cache_resource
def load_model():
    model = AdvancedMovieRecommender()
    model.run_pipeline()
    return model

model = load_model()

# -------------------------
# SIDEBAR (NEW UPGRADE)
# -------------------------
st.sidebar.title("⚙️ Filters")

user_id = st.sidebar.number_input("User ID", min_value=1, max_value=943, value=42)
top_n = st.sidebar.slider("Number of Movies", 1, 12, 6)

min_score = st.sidebar.slider("Minimum Score", 0.0, 5.0, 0.0)

# -------------------------
# GENRE FILTER
# -------------------------
genres = [
    "Action", "Adventure", "Animation", "Children",
    "Comedy", "Crime", "Documentary", "Drama",
    "Fantasy", "Horror", "Romance", "Sci-Fi"
]

selected_genre = st.sidebar.selectbox("Filter by Genre", ["All"] + genres)

# -------------------------
# SEARCH BAR (NEW)
# -------------------------
search_query = st.text_input("🔍 Search Movies (optional)")

# -------------------------
# HEADER
# -------------------------
st.title("🎬 AI Movie Recommendation System")
st.markdown("Netflix-style personalized recommendations powered by AI")

# -------------------------
# GENERATE BUTTON
# -------------------------
if st.button("Generate Recommendations"):

    recs = model.recommend_movies(user_id, top_n=50)  # get more first

    # -------------------------
    # FILTERING LOGIC
    # -------------------------
    filtered = []

    for movie in recs:

        # score filter
        if movie["predicted_score"] < min_score:
            continue

        # genre filter
        if selected_genre != "All":
            if selected_genre not in movie["genres"]:
                continue

        # search filter
        if search_query:
            if search_query.lower() not in movie["title"].lower():
                continue

        filtered.append(movie)

    st.success(f"Found {len(filtered)} recommendations")

    # -------------------------
    # GRID UI
    # -------------------------
    cols = st.columns(3)

    for i, movie in enumerate(filtered[:top_n]):

        with cols[i % 3]:

            if movie.get("poster"):
                st.image(movie["poster"], use_container_width=True)

            st.subheader(movie["title"])
            st.write(f"⭐ Score: {movie['predicted_score']}")

            if movie["genres"]:
                st.caption(", ".join(movie["genres"]))

            st.markdown("---")