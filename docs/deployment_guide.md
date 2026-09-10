# RetailPulse — Cloud Deployment & Live Hosting Guide

This guide provides step-by-step instructions to deploy **RetailPulse** to production cloud platforms using free-tier services.

---

## 1. Zero-Friction Cloud Deployment Architecture

```
                                  ┌────────────────────────┐
                                  │ Streamlit Community    │
                                  │ Cloud (Dashboard)      │
                                  └───────────┬────────────┘
                                              │
                      ┌───────────────────────┴───────────────────────┐
                      ▼                                               ▼
         ┌────────────────────────┐                      ┌────────────────────────┐
         │ Render / Railway       │                      │ Neon / Supabase        │
         │ (FastAPI REST API)     │◄────────────────────►│ (Serverless Postgres)  │
         └────────────────────────┘                      └────────────────────────┘
```

---

## 2. Step 1: Push Repository to GitHub

1. Create a new repository on GitHub named `RetailPulse`:
   - Visibility: **Public**
2. In your local terminal, add the remote and push:
   ```bash
   git add .
   git commit -m "feat: complete production-grade RetailPulse platform"
   git branch -M main
   git remote add origin https://github.com/<YOUR-GITHUB-USERNAME>/RetailPulse.git
   git push -u origin main
   ```

---

## 3. Step 2: Deploy Frontend on Streamlit Community Cloud (Free)

**Streamlit Community Cloud** provides 100% free hosting directly linked to your GitHub repository.

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. Click **"New app"**.
3. Configure the deployment settings:
   - **Repository**: `Abhi-githubb/RetailPlus` (or your fork)
   - **Branch**: `master`
   - **Main file path**: `app/dashboard/app.py`
   - **App URL**: `retailpulse-analytics.streamlit.app` (or custom name)
4. *(Optional — For PostgreSQL)*: Under **"Advanced settings"** -> **"Secrets"**, add your PostgreSQL connection string:
   ```toml
   DATABASE_URL = "postgresql://user:password@your-postgres-host:5432/retailpulse_db"
   ```
   *(If omitted, the app automatically initializes an embedded SQLite warehouse with zero configuration).*
5. Click **"Deploy!"**.
6. *First-Launch Note*: The dashboard automatically detects cloud initialization, builds all 6 tables, ingests records, and compiles all 9 analytical views before executing any queries.

---

## 4. Step 3: Deploy Backend on Render (Free Tier)

Render provides free hosting for web services with automatic TLS, custom domains, and GitHub continuous deployment.

### Option A: 1-Click Render Blueprint (Recommended)
1. Sign up at [render.com](https://render.com).
2. Click **"New +"** -> **"Blueprint"**.
3. Connect your `RetailPulse` GitHub repository.
4. Render will automatically read `render.yaml` and provision:
   - `retailpulse-api` (Web Service running FastAPI on Python 3.12)
   - `retailpulse-postgres` (Managed PostgreSQL instance)
5. Click **"Apply"**.

### Option B: Manual Web Service Setup
1. Click **"New +"** -> **"Web Service"**.
2. Select your `RetailPulse` repo.
3. Settings:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python run_pipeline.py`
   - **Start Command**: `uvicorn app.api.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`
4. Environment Variables:
   - `PYTHON_VERSION`: `3.12.0`
   - `DATABASE_URL`: `sqlite:///data/retailpulse.db` (or your Postgres connection string)
5. Click **"Create Web Service"**.
6. Access Swagger docs at: `https://<your-render-url>.onrender.com/docs`.

---

## 5. Step 4: Optional Cloud PostgreSQL (Neon / Supabase)

If you prefer a dedicated managed PostgreSQL database:

1. Create a free account at [Neon.tech](https://neon.tech) or [Supabase.com](https://supabase.com).
2. Create a new database project named `retailpulse`.
3. Copy the Connection String:
   ```
   postgresql://user:password@ep-cool-snowflake-123456.us-east-2.aws.neon.tech/retailpulse?sslmode=require
   ```
4. Set `DATABASE_URL` in your Streamlit Cloud and Render settings:
   ```bash
   DATABASE_URL=postgresql://user:password@ep-cool-snowflake-123456.us-east-2.aws.neon.tech/retailpulse?sslmode=require
   ```
5. Run `python run_pipeline.py` once to populate the cloud database.

---

## 6. Step 5: Docker Container Deployment (Local or VPS)

To run the entire 3-tier architecture (PostgreSQL 16 + FastAPI + Streamlit) locally or on a cloud virtual machine (AWS EC2 / DigitalOcean / GCP):

```bash
# Clone the repository
git clone https://github.com/<YOUR-GITHUB-USERNAME>/RetailPulse.git
cd RetailPulse

# Launch all 3 services via Docker Compose
docker compose up -d

# Verify running containers
docker compose ps

# Access Services:
# - Streamlit Dashboard:  http://localhost:8501
# - FastAPI Swagger Docs: http://localhost:8000/docs
# - PostgreSQL Database:  localhost:5432
```
