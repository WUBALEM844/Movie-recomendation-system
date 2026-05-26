import streamlit as st
import pandas as pd
import numpy as np
from app import BookRecommender

# Page Configuration
st.set_page_config(page_title="የመጽሐፍ ምክረ-ሀሳብ ሲስተም", page_icon="📚", layout="wide")

# Initialize and Cache the Recommender Engine for ultra-fast load
@st.cache_resource
def load_recommender():
    engine = BookRecommender()
    engine.run_pipeline()
    return engine

try:
    recommender = load_recommender()
    
    # Sidebar Selection
    st.sidebar.header("⚙️ የተጠቃሚ መቆጣጠሪያ")
    
    # Theme Configuration (Light vs Dark Mode)
    theme_choice = st.sidebar.selectbox("🎨 የመተግበሪያው ገጽታ (Theme)፦", ["Light Mode ☀️", "Dark Mode 🌙"])
    
    # Set dynamic colors based on theme selection (True Deep Colors)
    if theme_choice == "Dark Mode 🌙":
        bg_color = "#0B0F19"       # Deep Dark Space Blue
        card_bg = "#111827"        # Dark Card Grey/Blue
        text_main = "#F9FAFB"      # Crisp White
        text_sub = "#9CA3AF"       # Muted Grey
        border_color = "#374151"   # Slate Border
        badge_bg = "#1E1B4B"       # Deep Purple/Indigo
        badge_text = "#C7D2FE"     # Light Indigo Text
        input_info = "#1F2937"     # Info Box Dark
    else:
        bg_color = "#F8FAFC"       # Clean Slate White
        card_bg = "#FFFFFF"        # Pure White Card
        text_main = "#0F172A"      # Dark Charcoal Text
        text_sub = "#64748B"       # Slate Muted Text
        border_color = "#E2E8F0"   # Light Border
        badge_bg = "#FEF3C7"       # Amber Yellow Badge
        badge_text = "#B45309"     # Dark Amber Text
        input_info = "#EFF6FF"     # Light Blue Info Box

    # Premium Modern UI Styling with Dynamic Themes & Streamlit Menu Cleaner
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* 1. HIDING STREAMLIT DEFAULT MENU & DEPLOY BUTTONS */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        .stDeployButton {{display:none !important;}}
        
        /* 2. Global Styles */
        * {{ font-family: 'Inter', sans-serif; }}
        .stApp {{ background-color: {bg_color} !important; color: {text_main} !important; }}
        
        /* 3. Titles */
        .main-title {{ font-size: 38px !important; font-weight: 800; color: {text_main}; text-align: center; margin-bottom: 5px; letter-spacing: -0.5px; }}
        .sub-title {{ font-size: 15px; color: {text_sub}; text-align: center; margin-bottom: 35px; }}
        h3 {{ color: {text_main} !important; }}
        
        /* 4. Left Column: User History Cards */
        .history-card {{ background: {card_bg}; padding: 16px; border-radius: 12px; border: 1px solid {border_color}; margin-bottom: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
        .history-title {{ font-size: 16px !important; font-weight: 600; color: {text_main}; }}
        .history-author {{ font-size: 13px; color: {text_sub}; margin-top: 2px; }}
        .rating-badge {{ display: inline-flex; align-items: center; background-color: {badge_bg}; color: {badge_text}; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; margin-top: 10px; }}
        
        /* 5. Right Column: AI Recommendation Grid (Fixed Uniform Heights) */
        .rec-grid-card {{ background: {card_bg}; border: 1px solid {border_color}; padding: 16px; border-radius: 16px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); display: flex; flex-direction: column; justify-content: space-between; height: 460px; margin-bottom: 20px; }}
        .img-container {{ height: 200px; overflow: hidden; border-radius: 10px; margin-bottom: 12px; display: flex; justify-content: center; align-items: center; background: {border_color}; }}
        .img-container img {{ max-height: 100%; object-fit: cover; }}
        .rec-title {{ font-size: 16px !important; font-weight: 700; color: {text_main}; line-height: 1.3; height: 42px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }}
        .rec-author {{ font-size: 13px; color: {text_sub}; margin-top: 4px; height: 18px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
        .score-badge {{ font-size: 12px; color: #059669; font-weight: 600; background: #ECFDF5; padding: 4px 8px; border-radius: 6px; display: inline-block; margin-top: 8px; }}
        
        /* 6. Read Button Link */
        .read-btn {{ display: block; text-align: center; margin-top: auto; padding: 10px 16px; background-color: #2563EB; color: white !important; text-decoration: none; border-radius: 10px; font-size: 13px; font-weight: 600; box-shadow: 0 2px 4px rgba(37,99,235,0.2); transition: all 0.2s ease; }}
        .read-btn:hover {{ background-color: #1D4ED8; box-shadow: 0 4px 8px rgba(29,78,216,0.3); text-decoration: none; }}
        
        /* 7. Custom Alert Messages */
        .info-msg {{ background-color: {input_info}; color: {text_main}; padding: 15px; border-radius: 10px; font-size: 14px; margin-bottom: 15px; border-left: 4px solid #3B82F6; }}
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-title">📚 Smart Book Recommendation System</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">ይህ መተግበሪያ የእርስዎን ምርጫ መሰረት በማድረግ ምርጥ መጽሐፍትን በ AI cosine similarity ሂሳባዊ ቀመር ይመክራል።</div>', unsafe_allow_html=True)
    st.markdown("---")

    if "custom_ratings" not in st.session_state:
        st.session_state.custom_ratings = {}

    mode = st.sidebar.radio("የመተግበሪያው ሁነታ (Mode)፦", ["በዳታሴት ተጠቃሚዎች ይሞክሩ", "አዲስ ተጠቃሚ ይፍጠሩ (ይፈልጉ እና ደረጃ ይስጡ)"])

    if mode == "በዳታሴት ተጠቃሚዎች ይሞክሩ":
        available_users = sorted(recommender.ratings_df["User-ID"].unique())
        selected_user = st.sidebar.selectbox("እባክዎ የተጠቃሚ ID ይምረጡ፡", available_users)
        
        user_ratings = recommender.ratings_df[recommender.ratings_df["User-ID"] == selected_user]
        user_books = pd.merge(user_ratings, recommender.books_df, on="ISBN")
    else:
        selected_user = 9999  
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔍 አዲስ መጽሐፍ ይፈልጉ")
        
        search_query = st.sidebar.text_input("የመጽሐፍ ስም ይጻፉ፦", "")
        
        all_books_list = recommender.books_df["Book-Title"].unique()
        filtered_books = [b for b in all_books_list if search_query.lower() in b.lower()] if search_query else []
        
        if filtered_books:
            chosen_book_title = st.sidebar.selectbox("የፈለጉትን መጽሐፍ ይምረጡ፦", filtered_books)
            rating_value = st.sidebar.slider("ለዚህ መጽሐፍ የሚሰጡት ደረጃ (⭐)፦", 1, 10, 8)
            
            if st.sidebar.button("ደረጃውን መዝግብ (Add Rating)"):
                chosen_isbn = recommender.books_df[recommender.books_df["Book-Title"] == chosen_book_title]["ISBN"].values[0]
                st.session_state.custom_ratings[chosen_isbn] = rating_value
                st.sidebar.success(f"📌 '{chosen_book_title}' በተሳካ ሁኔታ ተመዝግቧል!")
        elif search_query:
            st.sidebar.caption("❌ ተመሳሳይ መጽሐፍ አልተገኘም")

        if st.session_state.custom_ratings and st.sidebar.button("የሰጡትን ደረጃዎች በሙሉ አጽዳ (Reset)"):
            st.session_state.custom_ratings = {}
            st.rerun()

        custom_rows = []
        for isbn, rate in st.session_state.custom_ratings.items():
            b_row = recommender.books_df[recommender.books_df["ISBN"] == isbn]
            if not b_row.empty:
                custom_rows.append({
                    "User-ID": selected_user,
                    "ISBN": isbn,
                    "Book-Rating": rate,
                    "Book-Title": b_row["Book-Title"].values[0],
                    "Book-Author": b_row["Book-Author"].values[0] if "Book-Author" in b_row.columns else "Unknown"
                })
        user_books = pd.DataFrame(custom_rows)

        if not user_books.empty:
            recommender.ratings_df = recommender.ratings_df[recommender.ratings_df["User-ID"] != 9999]
            recommender.ratings_df = pd.concat([recommender.ratings_df, user_books[["User-ID", "ISBN", "Book-Rating"]]], ignore_index=True)
            recommender.prepare_matrices()
            recommender.train()

    num_recommendations = st.sidebar.slider("የሚመከሩ መጽሐፍት ብዛት፡", min_value=1, max_value=10, value=5)

    # Main UI Layout
    col1, col2 = st.columns([1, 2], gap="large")

    with col1:
        st.subheader("📖 ያነበቧቸው መጽሐፍት ታሪክ")
        if not user_books.empty:
            for idx, row in user_books.iterrows():
                st.markdown(f"""
                    <div class='history-card'>
                        <div class='history-title'>🔹 {row['Book-Title']}</div>
                        <div class='history-author'>ደራሲ፦ {row['Book-Author']}</div>
                        <div class='rating-badge'>⭐ {row['Book-Rating']} / 10</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<div class='info-msg'>💡 እባክዎ በግራ በኩል መጽሐፍ ፈልገው ደረጃ በመስጠት ምርጫዎትን ያክሉ!</div>", unsafe_allow_html=True)

    with col2:
        st.subheader("✨ የተመረጡ አዳዲስ የ AI መጽሐፍ ምክረ-ሀሳቦች")
        
        if mode == "አዲስ ተጠቃሚ ይፍጠሩ (ይፈልጉ እና ደረጃ ይስጡ)" and len(st.session_state.custom_ratings) == 0:
            st.markdown("<div class='info-msg'>👋 መጽሐፍትን ለመምከር መጀመሪያ በግራ በኩል ቢያንስ ለአንድ መጽሐፍ ደረጃ መስጠት አለብዎት።</div>", unsafe_allow_html=True)
        else:
            with st.spinner("ምርጥ መጽሐፍትን በማስላት ላይ..."):
                recommendations = recommender.recommend_books(user_id=int(selected_user), top_n=num_recommendations)
                
            if recommendations:
                cols = st.columns(3)
                for i, book in enumerate(recommendations):
                    col_idx = i % 3
                    with cols[col_idx]:
                        fallback_cover = "https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=150&auto=format&fit=crop&q=60"
                        
                        if "Harry Potter" in book['title']:
                            fallback_cover = "https://images.unsplash.com/photo-1618666012174-83b441c0bc76?w=150&auto=format&fit=crop&q=60"
                        elif "Hobbit" in book['title'] or "1984" in book['title']:
                            fallback_cover = "https://images.unsplash.com/photo-1461360370896-922624d12aa1?w=150&auto=format&fit=crop&q=60"
                        elif "Gatsby" in book['title']:
                            fallback_cover = "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=150&auto=format&fit=crop&q=60"
                        elif "Sapiens" in book['title'] or "Educated" in book['title']:
                            fallback_cover = "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=150&auto=format&fit=crop&q=60"

                        # Create clean title link for online library search
                        clean_title = book['title'].split(" Vol")[0].replace(' ', '+')
                        search_url = f"https://openlibrary.org/search?q={clean_title}"

                        # Dynamic HTML Injector for exact uniform spacing structure
                        st.markdown(f"""
                            <div class='rec-grid-card'>
                                <div class='img-container'>
                                    <img src='{fallback_cover}'>
                                </div>
                                <div class='rec-title'>{book['title']}</div>
                                <div class='rec-author'>ደራሲ፦ {book['author']}</div>
                                <div>
                                    <span class='score-badge'>🎯 ተዛማጅነት፦ {book['score']:.4f}</span>
                                </div>
                                <a href='{search_url}' target='_blank' class='read-btn'>📖 መጽሐፉን ያንብቡ</a>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("ለዚህ ተጠቃሚ የሚሆን ምክረ-ሀሳብ ማግኘት አልተቻለም።")

except Exception as e:
    st.error(f"መተግበሪያውን በማስነሳት ላይ ስህተት አጋጥሟል፦ {e}")