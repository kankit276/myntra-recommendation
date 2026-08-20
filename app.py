import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config.settings import settings

st.set_page_config(page_title="Myntra Discovery Engine", page_icon="🛍️", layout="wide")

@st.cache_data
def load_data():
    opp_path = settings.OPPORTUNITIES_PATH
    class_path = settings.CLASSIFIED_DATA_PATH
    
    opportunities = []
    classified = []
    if os.path.exists(opp_path):
        with open(opp_path, 'r') as f:
            opportunities = json.load(f)
    if os.path.exists(class_path):
        with open(class_path, 'r') as f:
            classified = json.load(f)
            
    return opportunities, classified

def main():
    st.title("🛍️ AI-Powered Discovery Engine (Myntra)")
    st.markdown("Analyze why users add items to their wishlist but do not purchase them.")
    
    opportunities, classified = load_data()
    
    if not opportunities or not classified:
        st.warning("No analyzed data found. Please run the pipeline first.")
        return
        
    df = pd.DataFrame(classified)
    
    # Sidebar Filters
    st.sidebar.header("Filters")
    platforms = st.sidebar.multiselect("Source Platform", options=df['source_platform'].unique(), default=df['source_platform'].unique())
    segments = st.sidebar.multiselect("User Segment", options=df['user_segment_clues'].unique(), default=df['user_segment_clues'].unique())
    
    # Filter Data
    filtered_df = df[df['source_platform'].isin(platforms) & df['user_segment_clues'].isin(segments)]
    
    if filtered_df.empty:
        st.info("No reviews match the selected filters.")
        return
        
    # Hero Stats
    st.header("Executive Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Analyzed Conversations", len(filtered_df))
    
    top_opp = opportunities[0] if opportunities else None
    if top_opp:
        col2.metric("Top Barrier", top_opp['name'])
        col3.metric("Affected Reviews", f"{top_opp['percentage']}%")
        
        st.info(f"**Key Finding**: {top_opp['name']} affects {top_opp['percentage']}% of analyzed users, primarily in the '{top_opp['top_segment']}' segment.")
    
    st.divider()
    
    # Opportunities Ranking
    st.header("Ranked Opportunity Areas")
    for opp in opportunities:
        with st.expander(f"Opportunity: {opp['name']} (Score: {opp['score']}/100)"):
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Frequency", f"{opp['components']['frequency']}/5")
            c2.metric("Severity", f"{opp['components']['severity']}/5")
            c3.metric("Closeness", f"{opp['components']['closeness']}/5")
            c4.metric("Segment Clarity", f"{opp['components']['segment_clarity']}/5")
            c5.metric("Solvability", f"{opp['components']['non_discount_solvability']}/5")
            
            st.write(f"**Top Unresolved Questions**: {', '.join(opp['missing_info'])}")
            
            st.markdown("**Evidence Quotes:**")
            for ev in opp['evidence']:
                st.markdown(f"> *{ev['quote']}* [Source]({ev['url']})")
                
    st.divider()
    
    # Charts
    st.header("Barrier Analysis")
    
    # Treemap of barriers
    barrier_counts = filtered_df.explode('purchase_barriers')['purchase_barriers'].value_counts().reset_index()
    barrier_counts.columns = ['Barrier', 'Count']
    barrier_counts = barrier_counts[barrier_counts['Barrier'] != 'not_applicable']
    
    if not barrier_counts.empty:
        fig = px.treemap(barrier_counts, path=['Barrier'], values='Count', title="Frequency of Purchase Barriers")
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
