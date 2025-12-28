import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer, util
import torch

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Dubai Vibe Navigator", page_icon="✨")

# 2. LOAD DATA
@st.cache_data
def load_data():
    df = pd.read_csv("dubai_places.csv")
    # Combine relevant columns to create a rich text for the AI to "read"
    df['combined_text'] = df['Name'] + " " + df['Category'] + " " + df['Location'] + " " + df['Vibe Description'] + " " + df['Hidden Search Tags']
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("CSV file not found. Upload 'dubai_places.csv'.")
    st.stop()

# 3. LOAD AI MODEL (Cached so it only runs once)
@st.cache_resource
def load_model():
    # 'all-MiniLM-L6-v2' is a tiny, fast model designed for semantic search
    return SentenceTransformer('all-MiniLM-L6-v2')

with st.spinner("Loading AI Brain..."):
    model = load_model()

# 4. PRE-CALCULATE EMBEDDINGS (Cached)
# We convert all 200 places into vector space once
@st.cache_data
def encode_places(_model, text_list):
    return _model.encode(text_list, convert_to_tensor=True)

# Create embeddings for all places in the CSV
place_embeddings = encode_places(model, df['combined_text'].tolist())

# 5. UI INTERFACE
st.title("✨ Dubai Vibe Navigator")
st.markdown("Search by **feeling** (e.g., 'I want to cry alone', 'First date romance', 'Code all night').")

query = st.text_input("What is your vibe?", placeholder="Type here...")

if query:
    # --- THE MAGIC HAPPENS HERE ---
    # 1. Convert User Query to Vector
    query_embedding = model.encode(query, convert_to_tensor=True)
    
    # 2. Calculate Cosine Similarity (Math match between query and all places)
    cos_scores = util.cos_sim(query_embedding, place_embeddings)[0]
    
    # 3. Get Top 5 Results
    top_results = torch.topk(cos_scores, k=5)
    
    st.write("---")
    st.subheader("🤖 AI Best Matches:")
    
    for score, idx in zip(top_results.values, top_results.indices):
        row = df.iloc[int(idx)]
        
        # Optional: Filter out low confidence matches
        if score < 0.25: 
            continue
            
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{row['Name']}** ({row['Category']})")
                st.caption(f"📍 {row['Location']}")
                st.write(f"_{row['Vibe Description']}_")
            with col2:
                st.metric(label="Match Score", value=f"{int(score*100)}%")
                st.markdown(f"[Maps ↗]({row['Google Maps Link']})")
            st.divider()

else:
    st.info("Waiting for your vibe...")