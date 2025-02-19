import streamlit as st
from create_stories import create_stories, init_db
from trends_visualization import trends_visualization

# Initialize the database
init_db()

# App title
st.title("Scrum Board App")

# Tab layout
tab1, tab2 = st.tabs(["Create Stories", "Trends Visualization"])

# Tab 1: Create Stories
with tab1:
    create_stories()

# Tab 2: Trends Visualization
with tab2:
    trends_visualization()
