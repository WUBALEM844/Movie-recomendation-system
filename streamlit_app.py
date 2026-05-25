import streamlit as st
import logging
from app import AdvancedMovieRecommender
from config import DISPLAY_GENRES, validate_config
from auth import full_page_auth, add_favorite_ui, add_watchlist_ui, list_user_collections

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="AI Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------
# DARK THEME STYLING
# -------------------------
st.markdown(
    """
    <style>
    :root {
        color-scheme: dark;
        supported-color-schemes: dark;
    }

    body, [data-testid='stAppViewContainer'], [data-testid='stSidebar'] {
        background: linear-gradient(180deg, #050816 0%, #12182f 40%, #0b1220 100%) !important;
        color: #f8fafc !important;
    }

    .movie-card {
        background: rgba(15, 23, 42, 0.92);
        border: 1px solid rgba(79, 70, 229, 0.24);
        border-radius: 22px;
        padding: 18px;
        margin-bottom: 18px;
        box-shadow: 0 18px 40px rgba(0, 0, 0, 0.35);
        transition: transform 0.2s ease;
    }

    .movie-card:hover {
        transform: translateY(-4px);
    }

    .score-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: #4338ca;
        color: #f8fafc;
        padding: 6px 12px;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.95rem;
        margin-top: 8px;
    }

    .genre-badge {
        background: rgba(99, 102, 241, 0.18);
        color: #e0e7ff;
        padding: 5px 12px;
        border-radius: 999px;
        font-size: 0.82rem;
        margin: 4px 4px 4px 0;
        display: inline-block;
    }

    .rating-stars {
        color: #fde68a;
        font-size: 1.05rem;
        letter-spacing: 0.03rem;
        margin: 0;
    }

    .stButton>button {
        background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 10px 25px rgba(59, 130, 246, 0.24);
    }

    .stButton>button:hover {
        background: linear-gradient(135deg, #5b21b6, #1d4ed8) !important;
    }

    [data-testid='stRadio'] label {
        border-radius: 999px;
        padding: 10px 20px;
        margin-right: 8px;
        border: 1px solid rgba(148, 163, 184, 0.24);
        background: rgba(15, 23, 42, 0.95);
        color: #cbd5e1;
    }

    [data-testid='stRadio'] input[type='radio']:checked + label {
        background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
        color: white !important;
        border-color: transparent !important;
        box-shadow: 0 12px 24px rgba(59, 130, 246, 0.25);
    }

    /* Top nav - Netflix-style tab bar */
    .top-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: linear-gradient(90deg,#050406 0%, #0b0b0b 100%) !important;
        padding: 8px 18px;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.6);
        margin-bottom: 14px;
    }

    .brand {
        font-size: 1.25rem;
        font-weight: 800;
        color: #eef2ff;
        padding-left: 6px;
    }

    .user-info {
        color: #cbd5e1;
        font-size: 0.95rem;
        text-align: right;
        padding-right: 6px;
    }

    [data-testid='stRadio'] {
        display: flex !important;
        gap: 6px;
        align-items: center;
        justify-content: center;
        background: transparent !important;
    }

    [data-testid='stRadio'] label {
        padding: 10px 14px;
        border-radius: 6px;
        color: #cbd5e1;
        background: transparent;
        font-weight: 700;
        cursor: pointer;
        transition: color 0.12s ease, transform 0.12s ease;
        position: relative;
    }

    [data-testid='stRadio'] input[type='radio'] { display: none; }

    [data-testid='stRadio'] label:hover { color: #fff; transform: translateY(-2px); }

    [data-testid='stRadio'] input[type='radio']:checked + label {
        color: #fff !important;
    }

    /* remove Streamlit default top padding on full-page views */
    [data-testid='stAppViewContainer'] .main .block-container {
        padding-top: 0px !important;
        padding-bottom: 0px !important;
    }
    [data-testid='stAppViewContainer'] .main {
        padding-top: 0px !important;
    }

    /* red underline indicator similar to Netflix */
    [data-testid='stRadio'] input[type='radio']:checked + label::after {
        content: '';
        position: absolute;
        left: 10%;
        right: 10%;
        bottom: -10px;
        height: 4px;
        background: linear-gradient(90deg, #e50914, #ff3b3b);
        border-radius: 4px;
        box-shadow: 0 6px 22px rgba(229, 9, 20, 0.25);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_resource
def load_model():
    try:
        with st.spinner("🔄 Initializing AI model and loading data..."):
            model = AdvancedMovieRecommender()
            model.run_pipeline()
            logger.info("Model loaded successfully")
            return model
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        st.error(f"❌ Failed to initialize the recommendation engine: {e}")
        return None

is_valid, message = validate_config()
if not is_valid:
    st.sidebar.warning(f"⚠️ {message}. Posters may not load.")

model = load_model()
if model is None:
    st.stop()

# -------------------------
# AUTHENTICATION (full-page)
# -------------------------
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    full_page_auth()

if not st.session_state.user:
    st.stop()

current_user = st.session_state.user
user_uid = current_user.get("localId") if current_user else None

# navigation state default
if "page" not in st.session_state:
    st.session_state.page = "Home"

# Top navigation bar container (styled as Netflix-like tabs)
nav_options = ["Home", "Browse Movies", "My Favorites", "Watchlist", "Account"]
with st.container():
    cols = st.columns([1, 6, 2])
    with cols[0]:
        st.markdown("<div class='brand'>🎬 AI Movie Recommender</div>", unsafe_allow_html=True)
    with cols[1]:
        current_page = st.radio(
            "",
            nav_options,
            index=nav_options.index(st.session_state.page) if st.session_state.page in nav_options else 0,
            horizontal=True,
            label_visibility="collapsed",
            key="nav_radio",
        )
        st.session_state.page = current_page
    with cols[2]:
        st.markdown(f"<div class='user-info'>✓ Signed in</div>", unsafe_allow_html=True)

st.markdown("<hr style='border:1px solid rgba(148, 163, 184, 0.08); margin-top:6px; margin-bottom:20px;'/>", unsafe_allow_html=True)

# Sidebar controls (shared)
st.sidebar.header("🛠️ Recommendation Controls")
user_id = st.sidebar.number_input(
    "User ID",
    min_value=1,
    max_value=943,
    value=42,
    help="Choose a user ID to personalize recommendations"
)

top_n = st.sidebar.slider(
    "Number of results",
    min_value=1,
    max_value=12,
    value=6,
    help="Select how many recommended movies to display"
)

min_score = st.sidebar.slider(
    "Minimum score",
    min_value=0.0,
    max_value=10.0,
    value=0.0,
    step=0.1,
    help="Only show movies with score above this threshold"
)

selected_genre = st.sidebar.selectbox(
    "Genre filter",
    ["All"] + DISPLAY_GENRES,
    help="Use genre filtering to narrow results"
)

search_query = st.sidebar.text_input(
    "Search movies",
    placeholder="Type a movie name...",
    help="Search recommendation titles by keyword"
)

# Page renderers

def render_home():
    st.markdown(
        """
        <div style='padding: 18px; background: rgba(30, 41, 59, 0.85); border-radius: 24px; border: 1px solid rgba(148, 163, 184, 0.18);'>
            <p style='margin:0; font-size:0.95rem; color:#c7d2fe;'>AI Recommendations • Dark UI • Movie posters • Search & filters</p>
            <h1 style='margin:0.35rem 0 0; font-size:2.8rem; color:#eef2ff;'>🎬 Discover Your Next Favorite Movie</h1>
            <p style='margin:10px 0 0; color:#cbd5e1; font-size:1rem;'>Personalized, AI-powered movie recommendations with poster cards, genre tags, and a modern dark interface.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("⭐ Most Popular Movies")
    popular_count = st.slider(
        "Show top popular movies",
        min_value=6,
        max_value=18,
        value=12,
        key="popular_count"
    )

    if st.button("Load Popular Movies", key="load_pop_home"):
        with st.spinner("Loading popular movies..."):
            try:
                popular = model.get_popular_movies(top_n=popular_count)
                cols = st.columns(3, gap="large")
                for idx, movie in enumerate(popular):
                    with cols[idx % 3]:
                        st.markdown("<div class='movie-card'>", unsafe_allow_html=True)
                        if movie.get("poster"):
                            st.image(movie["poster"], use_container_width=True)
                        st.markdown(f"<h3 style='margin: 12px 0 6px; color:#eef2ff;'>{movie['title']}</h3>", unsafe_allow_html=True)
                        if movie["genres"]:
                            genres_html = "".join(
                                f"<span class='genre-badge'>{genre}</span>"
                                for genre in movie["genres"]
                            )
                            st.markdown(genres_html, unsafe_allow_html=True)
                        else:
                            st.markdown("<p style='color:#94a3b8;'>Genre data unavailable</p>", unsafe_allow_html=True)
                        if user_uid:
                            fav_key = f"fav_pop_{user_uid}_{movie['movie_id']}_{idx}"
                            wl_key = f"wl_pop_{user_uid}_{movie['movie_id']}_{idx}"
                            if st.button("❤ Favorite", key=fav_key):
                                add_favorite_ui(user_uid, movie)
                            if st.button("➕ Watchlist", key=wl_key):
                                add_watchlist_ui(user_uid, movie)

                        st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                logger.error(f"Could not load popular movies: {e}")
                st.error(f"❌ {e}")


def render_recommendations():
    st.subheader("🎯 AI Recommendation Preview")
    st.write("Customize filters on the left and click the button below to generate a polished movie list with posters, ratings, and genres.")
    if st.button("Generate AI Recommendations", key="gen_recs"):
        with st.spinner("✨ Generating personalized recommendations..."):
            try:
                recs = model.recommend_movies(user_id, top_n=50)
                filtered = []

                for movie in recs:
                    if movie["predicted_score"] < min_score:
                        continue
                    if selected_genre != "All" and selected_genre not in movie["genres"]:
                        continue
                    if search_query and search_query.lower() not in movie["title"].lower():
                        continue
                    filtered.append(movie)

                if not filtered:
                    st.warning("No matching movies found. Try changing the filters or search term.")
                else:
                    st.success(f"Found {len(filtered[:top_n])} AI-driven recommendations")
                    cols = st.columns(3, gap="large")
                    for idx, movie in enumerate(filtered[:top_n]):
                        with cols[idx % 3]:
                            st.markdown("<div class='movie-card'>", unsafe_allow_html=True)
                            if movie.get("poster"):
                                st.image(movie["poster"], use_container_width=True)
                            st.markdown(f"<h3 style='margin: 12px 0 6px; color:#eef2ff;'>{movie['title']}</h3>", unsafe_allow_html=True)
                            score = movie["predicted_score"]
                            score_label = f"AI Score: {score:.2f}"
                            st.markdown(f"<div class='score-badge'>{score_label}</div>", unsafe_allow_html=True)
                            pseudo_rating = min(5, max(0, score / 2))
                            stars = "★" * int(pseudo_rating) + "☆" * (5 - int(pseudo_rating))
                            st.markdown(f"<p class='rating-stars'>{stars}</p>", unsafe_allow_html=True)
                            if movie["genres"]:
                                genres_html = "".join(
                                    f"<span class='genre-badge'>{genre}</span>"
                                    for genre in movie["genres"]
                                )
                                st.markdown(genres_html, unsafe_allow_html=True)
                            else:
                                st.markdown("<p style='color:#94a3b8;'>Genre data unavailable</p>", unsafe_allow_html=True)
                            if user_uid:
                                fav_key = f"fav_{user_uid}_{movie['movie_id']}_{idx}"
                                wl_key = f"wl_{user_uid}_{movie['movie_id']}_{idx}"
                                if st.button("❤ Favorite", key=fav_key):
                                    add_favorite_ui(user_uid, movie)
                                if st.button("➕ Watchlist", key=wl_key):
                                    add_watchlist_ui(user_uid, movie)

                            st.markdown("</div>", unsafe_allow_html=True)
                    with st.expander("How this AI recommendation works"):
                        st.write(
                            "The system uses item-based collaborative filtering to compare movies watched by the selected user with similar titles in the MovieLens dataset. "
                            "Recommendations are ranked by similarity score and shown alongside poster art, genre tags, and an AI-generated score."
                        )
            except Exception as e:
                logger.error(f"Recommendation generation failed: {e}")
                st.error(f"❌ Failed to generate recommendations: {e}")


def render_favorites():
    st.header("❤ Your Favorites")
    favs = list_user_collections(user_uid)[0]
    if not favs:
        st.info("You have no favorites yet. Add some from Recommendations or Popular Movies.")
    else:
        cols = st.columns(3, gap="large")
        for idx, movie in enumerate(favs):
            with cols[idx % 3]:
                st.markdown("<div class='movie-card'>", unsafe_allow_html=True)
                if movie.get("poster"):
                    st.image(movie["poster"], use_container_width=True)
                st.markdown(f"<h3 style='margin: 12px 0 6px; color:#eef2ff;'>{movie.get('title','Untitled')}</h3>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)


def render_watchlist():
    st.header("➕ Your Watchlist")
    wl = list_user_collections(user_uid)[1]
    if not wl:
        st.info("Your watchlist is empty. Add movies to watch later.")
    else:
        cols = st.columns(3, gap="large")
        for idx, movie in enumerate(wl):
            with cols[idx % 3]:
                st.markdown("<div class='movie-card'>", unsafe_allow_html=True)
                if movie.get("poster"):
                    st.image(movie["poster"], use_container_width=True)
                st.markdown(f"<h3 style='margin: 12px 0 6px; color:#eef2ff;'>{movie.get('title','Untitled')}</h3>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)


def render_profile():
    st.header("👤 Profile")
    st.write("✓ You are signed in")
    if st.button("Sign out"):
        st.session_state.user = None
        st.session_state.page = "Home"

# Router
page = st.session_state.page

if page == "Home":
    render_home()
elif page == "Browse Movies":
    render_recommendations()
elif page == "My Favorites":
    render_favorites()
elif page == "Watchlist":
    render_watchlist()
elif page == "Account":
    render_profile()
else:
    st.write("Page not found")

st.markdown("---")
st.markdown(
    """
    <div style='text-align:center; color:#cbd5e1; font-size:0.95rem;'>
        <p>AI Movie Recommendation System • Dark UI • Poster cards • Search & filters</p>
        <p>MovieLens 100K dataset | Item-based K-NN collaborative filtering</p>
    </div>
    """,
    unsafe_allow_html=True,
)
