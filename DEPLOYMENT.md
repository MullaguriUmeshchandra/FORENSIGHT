# 🚀 Deploying CyberForensics to Render

This guide walks you through deploying both the **FastAPI Backend** and the **React Vite Frontend** to [Render](https://render.com).

---

## ⚡ Option 1: 1-Click Blueprint Deployment (Recommended)

Render Blueprints let you deploy the full-stack system automatically from the included [`render.yaml`](./render.yaml).

### Steps:
1. **Push your code to GitHub / GitLab**.
2. Go to your **[Render Dashboard](https://dashboard.render.com/)**.
3. Click **New +** in the top navigation and select **Blueprint**.
4. Connect your GitHub repository (`CYBERFORENSICS-`).
5. Render will automatically detect `render.yaml` and configure:
   - **`cyberforensics-backend`** (Python Web Service)
   - **`cyberforensics-frontend`** (Static Site with SPA rewrite rules)
6. Click **Apply**.
7. Render will build and deploy both services. Once finished:
   - Frontend will be live at: `https://cyberforensics-frontend.onrender.com`
   - Backend API will be live at: `https://cyberforensics-backend.onrender.com`
   - Interactive Swagger API docs: `https://cyberforensics-backend.onrender.com/docs`

---

## 🛠️ Option 2: Manual Deployment via Render Dashboard

If you prefer to configure the services manually in the Render UI:

### Step 1: Deploy Backend Web Service
1. In Render Dashboard, click **New +** → **Web Service**.
2. Connect your Git repository.
3. Configure the following settings:
   - **Name**: `cyberforensics-backend`
   - **Root Directory**: `backend`
   - **Runtime**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free`
4. Add the following **Environment Variables**:
   | Key | Value |
   |---|---|
   | `PYTHON_VERSION` | `3.11.9` |
   | `JWT_SECRET` | *Click "Generate"* |
   | `CORS_ORIGINS` | `["*"]` |
   | `UPLOAD_DIR` | `./uploads` |
   | `REPORT_DIR` | `./reports` |
5. Click **Create Web Service** and copy your backend URL (e.g., `https://cyberforensics-backend.onrender.com`).

---

### Step 2: Deploy Frontend Static Site
1. In Render Dashboard, click **New +** → **Static Site**.
2. Connect the same Git repository.
3. Configure the following settings:
   - **Name**: `cyberforensics-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
4. In the **Redirects / Rewrites** tab:
   - **Source**: `/*`
   - **Destination**: `/index.html`
   - **Action**: `Rewrite`
5. Add the following **Environment Variable**:
   | Key | Value |
   |---|---|
   | `VITE_API_BASE_URL` | `https://cyberforensics-backend.onrender.com/api` *(replace with your actual backend URL)* |
6. Click **Create Static Site**.

---

## 🔐 Default Login Credentials on Render

Once your frontend is deployed, open the frontend URL and log in with the pre-seeded credentials:

| Role | Username | Password |
|---|---|---|
| **Investigator** | `investigator` | `Investigator123!` |
| **Administrator** | `admin` | `Admin123!` |
| **Auditor / Viewer** | `viewer` | `Viewer123!` |

---

## 💾 Optional: Persistent Storage & PostgreSQL

### Using Render PostgreSQL (Recommended for production data persistence)
1. In Render Dashboard, click **New +** → **PostgreSQL**.
2. Create a free database (e.g. `cyberforensics-db`).
3. Copy the **Internal Database URL**.
4. In your `cyberforensics-backend` Web Service → **Environment**, set:
   - `DATABASE_URL` = `<your-render-postgresql-url>`
5. Deploying will automatically initialize all forensic tables on PostgreSQL.

---

## 🔍 Verification & Health Check

You can verify the deployed backend at any time by visiting:
`https://cyberforensics-backend.onrender.com/health`

Response:
```json
{
  "status": "healthy",
  "service": "AI Forensics Timeline Reconstruction Backend",
  "database": "connected",
  "neo4j": "offline (resilient fallback active)"
}
```
