import pandas as pd
import streamlit as st

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    # display cleaning options in streamlit streamlit and return the cleaned DataFrame.

    st.sidebar.subheader("Data Cleaning Tools")

    # 1. Handle Missing Values
    st.sidebar.subheader("Handle Missing Values")
    # show total missing values
    total_missing = df.isna().sum().sum()
    st.sidebar.write(f"Total Missing Values: **{total_missing}**")

    clean_option = st.sidebar.radio(
        "Choose how to handle missing values:",
        ("Do Nothing", "Drop Rows", "Drop Columns", "Fill with Mean (Numeric)", "Fill with Median (Numeric)", "Fill with Mode")
    )
    if clean_option == "Drop Rows":
        df = df.dropna()
        st.sidebar.success("Dropped all rows with missing values.")
    elif clean_option == "Drop Columns":
        df = df.dropna(axis=1)
        st.sidebar.success("Dropped all columns with missing values.")
    elif clean_option == "Fill with Mean (Numeric)":
        df = df.fillna(df.mean(numeric_only=True))
        st.sidebar.success("Filled missing numeric values with mean.")
    elif clean_option == "Fill with Median (Numeric)":
        df = df.fillna(df.median(numeric_only=True))
        st.sidebar.success("Filled missing numeric values with median.")
    elif clean_option == "Fill with Mode":
        df = df.fillna(df.mode().iloc[0])
        st.sidebar.success("Filled missing values with mode.")

    # 2. Remove Duplicates
    st.sidebar.subheader("Remove Duplicates")
    if st.sidebar.button("Remove Duplicates Rows"):
        before = len(df)
        df = df.drop_duplicates()
        after = len(df)
        st.sidebar.success(f"Removed {before - after} duplicate rows.")
    
    #  3. Confirm cleaning done
    st.sidebar.markdown("---")
    st.sidebar.info("Cleaning complete. Return to main view to re-analyze your data.")
    return df