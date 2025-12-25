import streamlit as st
import pandas as pd

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="Dubai Vibe Navigator",
    page_icon="✨",
    layout="centered"
)

# 2. LOAD DATA
# We use @st.cache_data so it doesn't reload the CSV every time you search (fast!)
@st.cache_data
def load_data():
    return pd.read_csv("dubai_places.csv")

try:
    df = load_data()
except FileNotFoundError:
    st.error("CSV file not found. Please make sure 'dubai_places.csv' is in the same folder.")
    st.stop()

# 3. THE UI (User Interface)
st.title("✨ Dubai Vibe Navigator")
st.markdown("Don't search by name. **Search by feeling.**")
st.markdown("*(Try: 'Quiet place to study', 'Romantic dinner', 'Loud party', 'Forest')*")

# Search Bar
query = st.text_input("What is your vibe today?", placeholder="Type a feeling...")

# 4. THE "AI" LOGIC
# This filters the data based on the "Hidden Search Tags" column
if query:
    # Filter: Check if query is in 'Hidden Search Tags' OR 'Vibe Description' (Case insensitive)
    results = df[
        df['Hidden Search Tags'].str.contains(query, case=False, na=False) | 
        df['Vibe Description'].str.contains(query, case=False, na=False)
    ]
    
    st.write(f"Found **{len(results)}** places matching your vibe:")
    
    # Display Results as Cards
    for index, row in results.iterrows():
        with st.container():
            st.markdown("---")
            st.subheader(f"{row['Name']} ({row['Category']})")
            st.caption(f"📍 {row['Location']}")
            st.write(f"_{row['Vibe Description']}_")
            st.markdown(f"[🗺️ Open in Google Maps]({row['Google Maps Link']})")
else:
    # If no search, show a few random suggestions
    st.markdown("---")
    st.write("### 🎲 Random Suggestions")
    sample = df.sample(3)
    for index, row in sample.iterrows():
        with st.container():
            st.markdown("---")
            st.subheader(f"Try: {row['Name']}")
            st.caption(row['Vibe Description'])

# Footer
st.markdown("---")
st.caption("Built with AI & Streamlit")