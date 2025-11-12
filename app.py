import streamlit as st
import pandas as pd
import os
import bcrypt
import uuid
from datetime import datetime
import json

from db import get_session, engine, Base
from models import User, Dataset, AnalysisHistory
from analyzer import analyze_csv
from cleaner import clean_data

# intial setup
# Create database tables if they don't exist
Base.metadata.create_all(bind=engine)

# streamlit page setup
st.set_page_config(page_title="Vizion", page_icon=":bar_chart:", layout="wide")
st.title("Vizion :bar_chart:")

session = get_session()

params = st.query_params
if "uid" in params and st.session_state.get("user_id") is None:
    uid = params["uid"]
    if isinstance(uid, list):
        uid = uid[0]
    user = session.query(User).filter_by(id=uid).first()
    if user:
        st.session_state.user_id = user.id
        st.session_state.email = user.email

st.sidebar.header("Login or Register")

if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "email" not in st.session_state:
    st.session_state.email = None

if st.session_state.user_id is None:
    tab_login, tab_register = st.sidebar.tabs(["Login", "Register"])

    with tab_register:
        st.subheader("Create your New Account")
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        pwd = st.text_input("Password", type="password")

        if st.button("Register"):
            if not name or not email or not pwd:
                st.error("Please fill empty fields.")
            else:
                existing_user = session.query(User).filter_by(email=email).first()
                if existing_user:
                    st.error("User with this email already exists.")
                else:
                    hashed_pwd = bcrypt.hashpw(
                        pwd.encode("utf-8"),
                        bcrypt.gensalt()
                    ).decode("utf-8")
                    new_user = User(
                        id=str(uuid.uuid4()),
                        name=name,
                        email=email,
                        password_hash=hashed_pwd
                    )
                    session.add(new_user)
                    session.commit()
                    st.success("New account created! You can now log in.")

    with tab_login:
        st.subheader("Log in to your Account")
        email_login = st.text_input("Email", key="login_email")
        pwd_login = st.text_input("Password", type="password", key="login_pwd")

        if st.button("Login"):
            user = session.query(User).filter_by(email=email_login).first()
            if user and bcrypt.checkpw(
                pwd_login.encode("utf-8"),
                user.password_hash.encode("utf-8")
            ):
                st.session_state.user_id = user.id
                st.session_state.email = user.email
                st.experimental_set_query_params(uid=user.id)
                st.success(f"Welcome back, {user.name}!")
                st.rerun()
            else:
                st.error("Invalid email or password.")

if st.session_state.user_id:
    user = session.query(User).filter_by(id=st.session_state.user_id).first()
    st.sidebar.write(f"Logged in as: {user.email}")

    if st.sidebar.button("Logout"):
        st.session_state.user_id = None
        st.session_state.email = None
        try:
            st.query_params.clear()
        except Exception:
            st.experimental_set_query_params()
        st.rerun()

    st.header("Your Analysis History")

    user_analyses = (
        session.query(AnalysisHistory)
        .filter_by(user_id=user.id)
        .order_by(AnalysisHistory.created_at.desc())
        .all()
    )

    cleaned_analyses = []
    dirty = False
    for a in user_analyses:
        if a.dataset is None or not os.path.exists(getattr(a.dataset, "storage_path", "")):
            session.delete(a)
            dirty = True
        else:
            cleaned_analyses.append(a)
    if dirty:
        session.commit()
    user_analyses = cleaned_analyses

    col_hist_left, col_hist_right = st.columns([1, 1])
    with col_hist_left:
        if st.button("Clear All History") and user_analyses:
            session.query(AnalysisHistory).filter_by(user_id=user.id).delete()
            session.query(Dataset).filter_by(user_id=user.id).delete()
            session.commit()
            st.success("All analysis history deleted.")
            st.rerun()
    with col_hist_right:
        pass

    if user_analyses:
        for a in user_analyses:
            ds = a.dataset
            label = ds.filename if ds else "[Missing dataset]"
            with st.expander(f"{label} — {a.created_at.strftime('%Y-%m-%d %H:%M:%S')}"):
                st.markdown(f"**Summary:** {a.summary}")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Open / Edit", key=f"open_{a.id}"):
                        st.session_state.editing_analysis_id = a.id
                        st.rerun()
                with c2:
                    if st.button("Delete", key=f"delete_{a.id}"):
                        session.delete(a)
                        session.commit()
                        st.success("Analysis deleted.")
                        st.rerun()
    else:
        st.info("No analysis history found. Upload and analyze a dataset to get started!")

    st.header("Upload your CSV File to Analyze")

    uploaded = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded is not None:
        filename = uploaded.name

        try:
            uploaded.seek(0)
        except Exception:
            pass
        try:
            df = pd.read_csv(uploaded)
        except UnicodeDecodeError:
            uploaded.seek(0)
            df = pd.read_csv(uploaded, encoding="latin-1")
        except Exception as e:
            st.error(f"Error reading file: {e}")
            st.stop()

        st.success(f"File '{filename}' uploaded successfully!")
        st.write("Preview of your file:")
        st.dataframe(df.head())

        original_csv_bytes = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="💾 Download Original CSV",
            data=original_csv_bytes,
            file_name=filename,
            mime="text/csv"
        )

        st.header("Analyze this Dataset (Original)")
        current_config_initial = st.session_state.get("current_viz_config")
        current_config = analyze_csv(
            df.copy(),
            key_prefix="current",
            initial_config=current_config_initial
        )
        st.session_state.current_viz_config = current_config

        if st.button("Save this Analysis"):
            dataset_id = str(uuid.uuid4())
            os.makedirs("data", exist_ok=True)
            dataset_dir = os.path.join("data", dataset_id)
            os.makedirs(dataset_dir, exist_ok=True)
            csv_path = os.path.join(dataset_dir, "original.csv")
            df.to_csv(csv_path, index=False)

            dataset = Dataset(
                id=dataset_id,
                user_id=user.id,
                filename=filename,
                storage_path=csv_path,
                row_count=len(df),
                column_count=len(df.columns),
                status="Saved",
                uploaded_at=datetime.utcnow()
            )
            session.add(dataset)

            insights_json = json.dumps(current_config) if current_config else None
            analysis = AnalysisHistory(
                id=str(uuid.uuid4()),
                dataset_id=dataset.id,
                user_id=user.id,
                created_at=datetime.utcnow(),
                summary=f"Analyzed '{filename}' with {len(df)} rows and {len(df.columns)} columns.",
                insights=insights_json
            )
            session.add(analysis)
            session.commit()
            st.success("Analysis history saved.")
            st.session_state.editing_analysis_id = analysis.id
            st.rerun()

        st.header("Clean your Data (Optional)")
        cleaned_df = clean_data(df.copy())
        if not cleaned_df.equals(df):
            st.header("Analyze Cleaned Data")
            analyze_csv(cleaned_df, key_prefix="cleaned")
        else:
            st.info("Cleaning did not change the data.")

        cleaned_csv_bytes = cleaned_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="💾 Download Cleaned CSV",
            data=cleaned_csv_bytes,
            file_name="cleaned_data.csv",
            mime="text/csv"
        )

    editing_id = st.session_state.get("editing_analysis_id")
    if editing_id:
        a = session.query(AnalysisHistory).filter_by(id=editing_id, user_id=user.id).first()
        if not a or not a.dataset or not os.path.exists(a.dataset.storage_path):
            st.warning("Saved dataset not found for this analysis.")
        else:
            st.header(f"Edit Saved Analysis: {a.dataset.filename}")
            df_edit = pd.read_csv(a.dataset.storage_path)
            try:
                initial_config = json.loads(a.insights) if a.insights else None
            except Exception:
                initial_config = None
            new_config = analyze_csv(
                df_edit,
                key_prefix=f"edit_{a.id}",
                initial_config=initial_config
            )
            if st.button("Save Changes", key=f"save_changes_{a.id}"):
                a.insights = json.dumps(new_config)
                session.commit()
                st.success("Analysis updated.")
                st.rerun()
