# 🚀 Deploying Store Inventory System (SIS) to Vercel

This guide will walk you through deploying your Flask backend to **Vercel** with a persistent database.

## 📋 Prerequisites
1. A **Vercel** account (connected to GitHub).
2. A **GitHub** repository containing this project.

## 🛠️ Configuration Files Created
I have already added the necessary configurations:
1. **`vercel.json`**: Configures the Python runtime, routes, and environment.
2. **`app.py` modifications**: 
   - Handled serverless logging (STDOUT).
   - Configured ephemeral file uploads (`/tmp`).
   - Added automatic database initialization for Postgres.

---

## 🚀 Step-by-Step Deployment

### 1. Push Code to GitHub
Ensure all your changes (including the new `vercel.json`) are on GitHub:
```bash
git add .
git commit -m "Configure for Vercel deployment"
git push origin main
```

### 2. Import Project to Vercel
1. Go to [Vercel Dashboard](https://vercel.com/dashboard).
2. Click **Add New** > **Project**.
3. Import your GitHub repository.

### 3. Connect a Database (CRITICAL)
Vercel serverless functions are stateless. **SQLite will not work** for saving data permanently.
1. In your Vercel project, go to the **Storage** tab.
2. Select **Connect Database** > **Vercel Postgres**.
3. Follow the steps to create a new database.
4. Once created, click **Connect**. This will automatically add `POSTGRES_URL` and other environment variables to your project.
5. In your Vercel **Environment Variables** settings, add a new key:
   - `DATABASE_URL`: Set it to the value of `POSTGRES_URL` (the one starting with `postgres://`).

### 4. Set Environment Variables
Go to **Settings** > **Environment Variables** and add:
- `SECRET_KEY`: A long random string.
- `ADMIN_PASSWORD`: Your desired password for the `admin` account (defaults to `admin`).
- `LOG_TO_STDOUT`: `true`

### 5. Deploy
1. Go to the **Deployments** tab.
2. Click the three dots on your latest deployment and select **Redeploy**.
3. Once finished, your app will be live at `your-project-name.vercel.app`!

---

## ⚠️ Important Notes for Vercel
- **Statelessness**: Files uploaded to the app are saved in `/tmp` and **will be deleted** when the serverless function cold-starts. For permanent storage, consider using an external service like Cloudinary or AWS S3.
- **Cold Starts**: The first request after some time might take a few seconds as the function "wakes up".
- **Database**: Ensure you have connected **Vercel Postgres** for "backend functioning properly".

---
> [!TIP]
> **Why Vercel?** It's extremely fast for frontend-heavy apps and provides a great developer experience with automatic SSL and preview deployments.
