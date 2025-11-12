import streamlit as st

def app_header(title: str):
    st.markdown(f"<h1 style='text-align:center; color:#00ADB5;'>{title}</h1>", unsafe_allow_html=True)
    st.markdown("---")

def sidebar_nav():
    return st.sidebar.radio("Navigation", ["Upload & Analyze", "History", "Profile", "Settings"])

def section_title(text: str):
    st.markdown(f"### {text}")
