import streamlit as st

st.set_page_config(
    page_title="Sales Predictor",
    page_icon="🚗",
    layout="wide"
)

left_co, cent_co, last_co = st.columns(3)
with cent_co:
    st.image("rising_tide_horizontal.png", use_container_width=False)
st.markdown("------------")

st.markdown(
    "<h1 style='text-align: center; color: white;'>Rising Tide Car Wash Daily Sales Predictor</h1>",
    unsafe_allow_html=True
)
st.markdown("---")
st.markdown(
    "<h3 style='text-align: center; color: white;'>Please select which Location to view from the sidebar</h3>",
    unsafe_allow_html=True
)
st.markdown("---")
with st.expander("📘 How it works", expanded=True):
    st.markdown("""
    **📍 Step 1**: Choose the location from the sidebar.  
    
    **📍 Step 2**: Enter total car count from yesterday, find this on: *WashConnect > Vehicle Performance*.
    
    **📍 Step 3**: Click `Predict` to fetch weather & generate your forecast.
    """)
