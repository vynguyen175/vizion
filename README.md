# Vizion - ML Analysis Platform

## Quick Deploy to Streamlit Cloud

### Step 1: Setup PostgreSQL Database (Free)

**Option A: Supabase (Recommended)**
1. Go to https://supabase.com
2. Create free account
3. Create new project
4. Go to Settings > Database
5. Copy the "Connection string" (URI format)
6. It looks like: `postgresql://postgres:[password]@[host]:5432/postgres`

**Option B: ElephantSQL**
1. Go to https://www.elephantsql.com
2. Create free "Tiny Turtle" instance
3. Copy the URL

### Step 2: Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io
2. Click "New app"
3. Select your repository and branch
4. Set Main file path: `app.py`
5. Click "Advanced settings"
6. In "Secrets" section, add:
```toml
DATABASE_URL = "your_postgresql_url_here"
```
7. Click "Deploy"

### Step 3: Wait for Deployment

First deployment takes 5-10 minutes. Watch the logs for any errors.

### Troubleshooting

**If you see 404 error:**
- Wait a few minutes - deployment might still be in progress
- Check the logs in Streamlit Cloud dashboard
- Make sure `app.py` is in the root of your repository

**If deployment fails:**
- Check that all files committed to GitHub
- Verify requirements.txt has all dependencies
- Check deployment logs for specific errors

**If you want to test without database:**
- The app will work with SQLite locally
- On Streamlit Cloud, data will reset on restart (not recommended for production)

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run migration
python migrate_database.py

# Run app
streamlit run app.py
```

## Architecture

- **Frontend**: Streamlit
- **Backend**: Python, SQLAlchemy
- **Database**: SQLite (local) / PostgreSQL (cloud)
- **ML**: scikit-learn, Papermill
- **Reports**: ReportLab, nbconvert

## Key Features

- CSV upload and analysis
- Automated ML notebook generation
- Multiple ML models (classification & regression)
- PDF and HTML report generation
- Column type auto-detection
- Model performance visualization
