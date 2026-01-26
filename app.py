import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime
import json

from db import get_session, engine, Base
from models import User, Dataset, AnalysisHistory
from analyzer import analyze_csv, display_column_types, detect_column_types
from cleaner import clean_data
from notebook_generator import generate_ml_notebook, suggest_ml_task
from notebook_runner import execute_notebook, get_execution_summary, convert_notebook_to_python, convert_notebook_to_html
from report_generator import generate_model_card_pdf, generate_html_report
from components.auth import render_auth_sidebar
from components.notifications import (
    send_welcome_email, 
    send_analysis_complete_email, 
    send_ml_notebook_ready_email,
    can_send_notification,
    mark_notification_sent
)

def inject_pro_theme_css():
    """Inject comprehensive theme CSS with light/dark mode support."""

    # Initialize theme in session state
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'

    theme = st.session_state.theme

    st.markdown(
        f"""
        <style>
        /* Import Inter font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* CSS Variables */
        :root {{
            --primary: #0D9488;
            --primary-light: #14B8A6;
            --primary-dark: #0F766E;
            --success: #10B981;
            --warning: #F59E0B;
            --error: #EF4444;
            --info: #3B82F6;
        }}

        /* Light theme variables */
        .light-theme {{
            --bg-primary: #F8FAFC;
            --bg-secondary: #F1F5F9;
            --bg-card: #FFFFFF;
            --text-primary: #0F172A;
            --text-secondary: #64748B;
            --text-muted: #94A3B8;
            --border-color: #E2E8F0;
            --shadow: 0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06);
            --shadow-lg: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
        }}

        /* Dark theme variables */
        .dark-theme {{
            --bg-primary: #0F172A;
            --bg-secondary: #1E293B;
            --bg-card: #1E293B;
            --text-primary: #F8FAFC;
            --text-secondary: #94A3B8;
            --text-muted: #64748B;
            --border-color: #334155;
            --shadow: 0 1px 3px rgba(0,0,0,0.3), 0 1px 2px rgba(0,0,0,0.2);
            --shadow-lg: 0 4px 6px -1px rgba(0,0,0,0.3), 0 2px 4px -1px rgba(0,0,0,0.2);
        }}

        /* Apply theme class to root */
        .stApp {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }}

        /* Main container */
        .block-container {{
            max-width: 1200px;
            padding-top: 1rem;
            padding-bottom: 4rem;
        }}

        /* Headers */
        h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
            font-family: 'Inter', sans-serif !important;
            font-weight: 700 !important;
        }}

        /* Cards styling */
        .stExpander, [data-testid="stExpander"] {{
            background-color: var(--bg-card) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 12px !important;
            box-shadow: var(--shadow) !important;
            overflow: hidden;
        }}

        .streamlit-expanderHeader {{
            font-weight: 600 !important;
            font-family: 'Inter', sans-serif !important;
        }}

        /* Metric cards */
        [data-testid="metric-container"] {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1rem;
            box-shadow: var(--shadow);
        }}

        [data-testid="stMetricValue"] {{
            font-family: 'Inter', sans-serif !important;
            font-weight: 700 !important;
            color: var(--primary) !important;
        }}

        [data-testid="stMetricLabel"] {{
            font-family: 'Inter', sans-serif !important;
            font-weight: 500 !important;
            text-transform: uppercase;
            font-size: 0.75rem !important;
            letter-spacing: 0.05em;
        }}

        /* Buttons - Pill shaped with teal accent */
        .stButton > button {{
            font-family: 'Inter', sans-serif !important;
            border-radius: 9999px !important;
            padding: 0.5rem 1.5rem !important;
            font-weight: 600 !important;
            font-size: 0.875rem !important;
            border: 1px solid var(--primary) !important;
            background-color: transparent !important;
            color: var(--primary) !important;
            transition: all 0.2s ease !important;
            box-shadow: var(--shadow) !important;
        }}

        .stButton > button:hover {{
            background-color: var(--primary) !important;
            color: white !important;
            box-shadow: var(--shadow-lg) !important;
            transform: translateY(-1px);
        }}

        .stButton > button[kind="primary"],
        .stButton > button[data-testid="baseButton-primary"] {{
            background-color: var(--primary) !important;
            color: white !important;
            border-color: var(--primary) !important;
        }}

        .stButton > button[kind="primary"]:hover,
        .stButton > button[data-testid="baseButton-primary"]:hover {{
            background-color: var(--primary-dark) !important;
            border-color: var(--primary-dark) !important;
        }}

        /* Download buttons */
        .stDownloadButton > button {{
            font-family: 'Inter', sans-serif !important;
            border-radius: 9999px !important;
            padding: 0.5rem 1.5rem !important;
            font-weight: 600 !important;
            border: 1px solid var(--primary) !important;
            background-color: var(--primary) !important;
            color: white !important;
            transition: all 0.2s ease !important;
        }}

        .stDownloadButton > button:hover {{
            background-color: var(--primary-dark) !important;
            box-shadow: var(--shadow-lg) !important;
        }}

        /* File uploader */
        [data-testid="stFileUploader"] {{
            background-color: var(--bg-card) !important;
            border: 2px dashed var(--border-color) !important;
            border-radius: 12px !important;
            padding: 1.5rem !important;
            transition: border-color 0.2s ease;
        }}

        [data-testid="stFileUploader"]:hover {{
            border-color: var(--primary) !important;
        }}

        /* Data frames / tables */
        .stDataFrame, [data-testid="stDataFrame"] {{
            border-radius: 12px !important;
            overflow: hidden !important;
            box-shadow: var(--shadow) !important;
            border: 1px solid var(--border-color) !important;
        }}

        .dataframe {{
            border-radius: 12px !important;
        }}

        /* Selectbox and inputs */
        .stSelectbox > div > div,
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {{
            border-radius: 8px !important;
            border-color: var(--border-color) !important;
            font-family: 'Inter', sans-serif !important;
        }}

        .stSelectbox > div > div:focus-within,
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {{
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 2px rgba(13, 148, 136, 0.2) !important;
        }}

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}

        .stTabs [data-baseweb="tab"] {{
            font-family: 'Inter', sans-serif !important;
            font-weight: 500 !important;
            border-radius: 8px !important;
            padding: 0.5rem 1rem !important;
        }}

        .stTabs [aria-selected="true"] {{
            background-color: var(--primary) !important;
            color: white !important;
        }}

        /* Info, success, warning, error boxes */
        .stAlert {{
            border-radius: 12px !important;
            font-family: 'Inter', sans-serif !important;
        }}

        /* Sidebar styling */
        [data-testid="stSidebar"] {{
            background-color: var(--bg-card) !important;
            border-right: 1px solid var(--border-color) !important;
        }}

        [data-testid="stSidebar"] .stMarkdown {{
            font-family: 'Inter', sans-serif !important;
        }}

        /* Progress bars and spinners */
        .stProgress > div > div {{
            background-color: var(--primary) !important;
        }}

        /* Checkbox */
        .stCheckbox label {{
            font-family: 'Inter', sans-serif !important;
        }}

        /* Custom card class */
        .vizion-card {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: var(--shadow);
            margin-bottom: 1rem;
        }}

        /* Stat card */
        .stat-card {{
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 1.25rem;
            box-shadow: var(--shadow);
        }}

        .stat-card .stat-label {{
            font-size: 0.625rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
        }}

        .stat-card .stat-value {{
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--text-primary);
        }}

        .stat-card .stat-trend {{
            font-size: 0.625rem;
            font-weight: 500;
            margin-top: 0.25rem;
        }}

        .stat-card .stat-trend.positive {{
            color: var(--success);
        }}

        .stat-card .stat-trend.negative {{
            color: var(--error);
        }}

        /* Section header */
        .section-header {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 1rem;
        }}

        .section-header .icon {{
            width: 2rem;
            height: 2rem;
            background-color: var(--primary);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }}

        .section-header h2 {{
            margin: 0;
            font-size: 1.125rem;
            font-weight: 700;
        }}

        /* Theme toggle button */
        .theme-toggle {{
            position: fixed;
            top: 0.75rem;
            right: 1rem;
            z-index: 1000;
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 9999px;
            padding: 0.5rem;
            cursor: pointer;
            box-shadow: var(--shadow);
            transition: all 0.2s ease;
        }}

        .theme-toggle:hover {{
            box-shadow: var(--shadow-lg);
        }}

        /* Divider */
        hr {{
            border: none;
            border-top: 1px solid var(--border-color);
            margin: 1.5rem 0;
        }}

        /* Links */
        a {{
            color: var(--primary) !important;
        }}

        a:hover {{
            color: var(--primary-dark) !important;
        }}
        </style>

        <!-- Apply theme class -->
        <script>
            const theme = '{theme}';
            const stApp = window.parent.document.querySelector('.stApp');
            if (stApp) {{
                stApp.classList.remove('light-theme', 'dark-theme');
                stApp.classList.add(theme + '-theme');
            }}
        </script>
        """,
        unsafe_allow_html=True,
    )


def render_theme_toggle():
    """Render theme toggle button in sidebar."""
    current_theme = st.session_state.get('theme', 'light')

    col1, col2 = st.sidebar.columns([3, 1])
    with col2:
        if current_theme == 'light':
            if st.button("Dark", key="theme_toggle", help="Switch to dark mode"):
                st.session_state.theme = 'dark'
                st.rerun()
        else:
            if st.button("Light", key="theme_toggle", help="Switch to light mode"):
                st.session_state.theme = 'light'
                st.rerun()

# intial setup
# Create database tables if they don't exist
Base.metadata.create_all(bind=engine)

# streamlit page setup
st.set_page_config(page_title="Vizion", page_icon=None, layout="wide")
inject_pro_theme_css()

# Styled header with logo
st.markdown(
    """
    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem;">
        <div style="
            width: 2.5rem;
            height: 2.5rem;
            background: linear-gradient(135deg, #0D9488 0%, #14B8A6 100%);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 1.25rem;
            font-family: 'Inter', sans-serif;
        ">V</div>
        <div>
            <h1 style="margin: 0; font-size: 1.75rem; font-weight: 700; font-family: 'Inter', sans-serif;">Vizion</h1>
            <p style="margin: 0; font-size: 0.875rem; color: #64748B; font-family: 'Inter', sans-serif;">Data Analysis & ML Platform</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

session = get_session()

# Render theme toggle and authentication sidebar
render_theme_toggle()
user = render_auth_sidebar(session, User)

# Only show main app if user is logged in
if user:

    with st.container():
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
    with st.container():
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
                label="Download Original CSV",
                data=original_csv_bytes,
                file_name=filename,
                mime="text/csv"
            )

            # Display column type detection
            display_column_types(df)
            
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
                
                # Send email notification
                if can_send_notification(user):
                    summary_html = f"<ul><li><strong>Rows:</strong> {len(df)}</li><li><strong>Columns:</strong> {len(df.columns)}</li></ul>"
                    if send_analysis_complete_email(user, filename, summary_html):
                        mark_notification_sent(session, user)
                
                st.session_state.editing_analysis_id = analysis.id
                st.rerun()

            # ML NOTEBOOK SECTION
            st.markdown("---")
            st.header("Generate ML Notebook & Analysis")
            
            st.info("**New Feature!** Automatically generate a Jupyter notebook with ML analysis, train models, and get professional reports.")
            
            with st.expander("What is this?", expanded=False):
                st.markdown("""
                This feature automatically:
                - Generates a complete Jupyter notebook with ML code
                - Performs advanced exploratory data analysis
                - Trains and evaluates machine learning models
                - Extracts feature importance
                - Provides professional PDF and HTML reports
                - Allows you to download the notebook for further customization
                """)
            
            # Column for target selection
            col_types = detect_column_types(df)
            all_columns = df.columns.tolist()
            
            # Target column selection
            st.subheader("Step 1: Select Target Column (Optional)")
            target_column = st.selectbox(
                "Choose the column you want to predict (leave as 'None' for EDA only):",
                options=["None (EDA Only)"] + all_columns,
                key="ml_target_column",
                help="Select the variable you want to predict. If you're not sure, choose 'None' for exploratory analysis."
            )
            
            target_column = None if target_column == "None (EDA Only)" else target_column
            
            # Suggest ML task
            if target_column:
                task_suggestion = suggest_ml_task(df, target_column)
                st.info(f"**Suggested Task:** {task_suggestion['task_type'].replace('_', ' ').title()}")
                st.caption(f"Reason: {task_suggestion['reason']}")
                task_type = task_suggestion['task_type']
            else:
                task_type = 'eda'
                st.info("**Mode:** Exploratory Data Analysis (No ML model training)")
            
            # Model selection (only if not EDA)
            model_type = None
            if task_type != 'eda':
                st.subheader("Step 2: Select Model (Optional)")
                
                if 'classification' in task_type:
                    model_options = {
                        "Auto-select (Recommended)": None,
                        "Logistic Regression": "logistic_regression",
                        "Random Forest": "random_forest",
                        "Gradient Boosting": "gradient_boosting",
                        "K-Nearest Neighbors": "knn"
                    }
                else:
                    model_options = {
                        "Auto-select (Recommended)": None,
                        "Linear Regression": "linear_regression",
                        "Ridge Regression": "ridge",
                        "Random Forest": "random_forest",
                        "Gradient Boosting": "gradient_boosting"
                    }
                
                selected_model = st.selectbox(
                    "Choose a model or let the system auto-select:",
                    options=list(model_options.keys()),
                    key="ml_model_selection"
                )
                model_type = model_options[selected_model]
                
                if model_type is None:
                    st.caption("Multiple models will be trained and the best one will be selected automatically.")
                else:
                    st.caption(f"Will use {selected_model}")
            
            # Generate and Execute button
            st.subheader("Step 3: Generate & Execute ML Notebook")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                generate_button = st.button("Generate & Run ML Analysis", type="primary", use_container_width=True)
            
            with col2:
                generate_only = st.button("Generate Notebook Only (Don't Execute)", use_container_width=True)
            
            if generate_button or generate_only:
                # Save CSV temporarily
                temp_dataset_id = str(uuid.uuid4())
                os.makedirs("data", exist_ok=True)
                temp_dataset_dir = os.path.join("data", temp_dataset_id)
                os.makedirs(temp_dataset_dir, exist_ok=True)
                temp_csv_path = os.path.join(temp_dataset_dir, "data.csv")
                df.to_csv(temp_csv_path, index=False)
                
                # Generate notebook
                notebook_path = os.path.join(temp_dataset_dir, "ml_analysis.ipynb")
                
                with st.spinner("Generating ML notebook..."):
                    try:
                        generate_ml_notebook(
                            csv_path=temp_csv_path,
                            output_path=notebook_path,
                            target_column=target_column,
                            model_type=model_type,
                            task_type=task_type
                        )
                        st.success("Notebook generated successfully!")
                        
                        # Provide download for generated notebook
                        with open(notebook_path, 'rb') as nb_file:
                            st.download_button(
                                label="Download Generated Notebook (.ipynb)",
                                data=nb_file,
                                file_name="ml_analysis.ipynb",
                                mime="application/x-ipynb+json",
                                key="download_generated_notebook"
                            )
                        
                        if generate_button:
                            # Execute notebook
                            st.subheader("Executing Notebook...")
                            executed_notebook_path = os.path.join(temp_dataset_dir, "ml_analysis_executed.ipynb")
                            
                            with st.spinner("Training models and analyzing data... This may take a minute."):
                                try:
                                    result = execute_notebook(
                                        notebook_path=notebook_path,
                                        output_notebook_path=executed_notebook_path
                                    )
                                    
                                    if result['success']:
                                        st.success("Analysis completed successfully!")
                                        
                                        # Display results
                                        st.markdown("---")
                                        st.header("Analysis Results")
                                        
                                        metrics = result.get('metrics', {})
                                        
                                        if task_type != 'eda':
                                            # Display metrics in cards
                                            st.subheader("Model Performance")
                                            
                                            if 'classification' in task_type:
                                                col1, col2, col3, col4 = st.columns(4)
                                                
                                                with col1:
                                                    acc = metrics.get('accuracy', 0)
                                                    st.metric("Accuracy", f"{acc:.2%}" if acc else "N/A")
                                                
                                                with col2:
                                                    prec = metrics.get('precision', 0)
                                                    st.metric("Precision", f"{prec:.2%}" if prec else "N/A")
                                                
                                                with col3:
                                                    rec = metrics.get('recall', 0)
                                                    st.metric("Recall", f"{rec:.2%}" if rec else "N/A")
                                                
                                                with col4:
                                                    f1 = metrics.get('f1_score', 0)
                                                    st.metric("F1-Score", f"{f1:.2%}" if f1 else "N/A")
                                            
                                            else:  # Regression
                                                col1, col2, col3 = st.columns(3)
                                                
                                                with col1:
                                                    r2 = metrics.get('r2_score', 0)
                                                    st.metric("R² Score", f"{r2:.4f}" if r2 else "N/A")
                                                
                                                with col2:
                                                    mae = metrics.get('mae', 0)
                                                    st.metric("MAE", f"{mae:.4f}" if mae else "N/A")
                                                
                                                with col3:
                                                    rmse = metrics.get('rmse', 0)
                                                    st.metric("RMSE", f"{rmse:.4f}" if rmse else "N/A")
                                            
                                            if metrics.get('model_name'):
                                                st.info(f"**Best Model:** {metrics['model_name']}")
                                        
                                        # Execution summary
                                        st.subheader("Summary")
                                        summary = get_execution_summary(metrics)
                                        st.markdown(summary)
                                        
                                        # Generate reports
                                        st.markdown("---")
                                        st.subheader("Download Results")
                                        
                                        col1, col2, col3, col4 = st.columns(4)
                                        
                                        with col1:
                                            # Download executed notebook
                                            with open(executed_notebook_path, 'rb') as nb_file:
                                                st.download_button(
                                                    label="Executed Notebook",
                                                    data=nb_file,
                                                    file_name="ml_analysis_executed.ipynb",
                                                    mime="application/x-ipynb+json",
                                                    key="download_executed_notebook"
                                                )
                                        
                                        with col2:
                                            # Convert to Python script
                                            py_script_path = os.path.join(temp_dataset_dir, "ml_analysis.py")
                                            if convert_notebook_to_python(executed_notebook_path, py_script_path):
                                                with open(py_script_path, 'rb') as py_file:
                                                    st.download_button(
                                                        label="Python Script",
                                                        data=py_file,
                                                        file_name="ml_analysis.py",
                                                        mime="text/x-python",
                                                        key="download_python_script"
                                                    )
                                        
                                        with col3:
                                            # Generate HTML report
                                            html_report_path = os.path.join(temp_dataset_dir, "model_report.html")
                                            dataset_info = {
                                                'rows': len(df),
                                                'columns': len(df.columns),
                                                'missing_values': df.isnull().sum().sum(),
                                                'numeric_features': len(col_types['numeric']),
                                                'categorical_features': len(col_types['categorical'])
                                            }
                                            ml_config = {
                                                'task_type': task_type,
                                                'target_column': target_column,
                                                'model_type': metrics.get('model_name', 'Auto-selected')
                                            }
                                            
                                            if generate_html_report(html_report_path, filename, dataset_info, ml_config, metrics, summary):
                                                with open(html_report_path, 'rb') as html_file:
                                                    st.download_button(
                                                        label="HTML Report",
                                                        data=html_file,
                                                        file_name="model_report.html",
                                                        mime="text/html",
                                                        key="download_html_report"
                                                    )
                                        
                                        with col4:
                                            # Generate PDF report
                                            pdf_report_path = os.path.join(temp_dataset_dir, "model_card.pdf")
                                            if generate_model_card_pdf(pdf_report_path, filename, dataset_info, ml_config, metrics):
                                                with open(pdf_report_path, 'rb') as pdf_file:
                                                    st.download_button(
                                                        label="PDF Model Card",
                                                        data=pdf_file,
                                                        file_name="model_card.pdf",
                                                        mime="application/pdf",
                                                        key="download_pdf_report"
                                                    )
                                        
                                        st.success("Complete ML pipeline executed successfully! Download your results above.")
                                        
                                        # Send email notification
                                        if can_send_notification(user):
                                            accuracy = metrics.get('accuracy') or metrics.get('r2_score')
                                            if send_ml_notebook_ready_email(user, filename, metrics.get('model_name', 'ML Model'), accuracy):
                                                mark_notification_sent(session, user)
                                    
                                    else:
                                        st.error(f"Notebook execution failed: {result.get('error', 'Unknown error')}")
                                        st.info("You can still download the generated notebook above and run it manually.")
                                
                                except Exception as e:
                                    st.error(f"Error during execution: {str(e)}")
                                    st.info("You can still download the generated notebook above and run it manually.")
                        
                    except Exception as e:
                        st.error(f"Error generating notebook: {str(e)}")
            
            st.markdown("---")
            
            st.header("Clean your Data (Optional)")
            cleaned_df = clean_data(df.copy())
            if not cleaned_df.equals(df):
                st.header("Analyze Cleaned Data")
                analyze_csv(cleaned_df, key_prefix="cleaned")
            else:
                st.info("Cleaning did not change the data.")

            cleaned_csv_bytes = cleaned_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Cleaned CSV",
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

else:
    # User not logged in - show welcome message
    st.info("Please log in or register to start analyzing your data with Vizion!")
    
    st.markdown("---")
    
    # Show features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Data Analysis")
        st.write("Upload CSV files and get instant insights with visualizations and statistics")
    
    with col2:
        st.subheader("ML Notebooks")
        st.write("Generate Jupyter notebooks with machine learning models tailored to your data")
    
    with col3:
        st.subheader("Professional Reports")
        st.write("Download PDF and HTML reports of your analyses")
