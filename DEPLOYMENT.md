# Deployment Guide: Store Inventory System (SIS)

This guide helps you deploy your SIS project to **Render** with a permanent **PostgreSQL** database.

## 🚀 Deployment Assets Created

I have already added the following essential files to your project:
1. **`Procfile`**: Tells hosting services how to run your web server.
2. **`build.sh`**: A script that installs dependencies and initializes the database during deployment.
3. **`render.yaml`**: A "Blueprint" file that automatically configures your web service, environment variables, and PostgreSQL database on Render.
4. **`requirements.txt`**: Added `gunicorn` (production-grade web server) and `psycopg2-binary` (PostgreSQL driver).

---

## 🛠 Step-by-Step Deployment

### 1. Push Your Code to GitHub
Your project already has a `.git` folder. Make sure your latest changes are pushed to a **GitHub repository**:

```bash
git add .
git commit -m "Prepare for deployment to Render"
git branch -M main
# Replace URL with your actual GitHub repository URL
git remote add origin https://github.com/yourusername/your-repo-name.git
git push -u origin main
```
*Note: If you already have a remote named 'origin', you may need to use `git push -u origin main` directly.*

### 2. Connect to Render
1. Go to [Render.com](https://render.com/) and log in with your GitHub account.
2. Click **New +** and select **Blueprint**.
3. Connect your GitHub repository.
4. Render will read the `render.yaml` file I created. It will automatically:
   - Create a **Web Service**.
   - Create a **PostgreSQL Database**.
   - Generate a secure `SECRET_KEY` and `ADMIN_PASSWORD`.

### 3. Configure Environment Variables (Optional)
If you need to use **Twilio SMS** or **Email** notifications in production:
1. In your Render Dashboard, go to your **Web Service** (`sis-inventory`).
2. Go to the **Environment** tab.
3. Add the following keys (values should come from your `.env`):
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_PHONE_NUMBER`
   - `MAIL_USERNAME`
   - `MAIL_PASSWORD`

### 4. Final Access
Once the build is complete:
- Your site will be live at `https://sis-inventory.onrender.com` (or similar).
- **Admin Access**: Find your generated `ADMIN_PASSWORD` in the Render dashboard under "Environment" for the web service.

---

> [!TIP]
> **Why Render?** It's free for individual projects, handles SSL (https) automatically, and the "Blueprint" feature means you don't have to manually click through complicated settings!

> [!WARNING]
> The "Free Tier" on Render puts your app to "sleep" after 15 minutes of inactivity. The first request after a long time might take 30–60 seconds to load while the server wakes up.
