# Deployment Guide

This project is configured to be deployed on **Vercel**, taking advantage of their serverless deployment model. Vercel will host both your React frontend (as static files) and your Python Flask backend (as Serverless Functions).

## 🚀 Prerequisites

1. A [GitHub](https://github.com/) account with this repository pushed to it.
2. A [Vercel](https://vercel.com/) account (you can sign up using your GitHub account).

## 📦 Project Configuration Details

Your repository is already pre-configured for Vercel deployment:
- **`vercel.json`**: This file is the heart of the deployment. It tells Vercel:
  - To use `@vercel/python` to build your `backend/app.py` into Serverless Functions.
  - To use `@vercel/static-build` to build your React frontend from `frontend/package.json`.
  - How to route `/api/*` requests to your backend and other requests to your frontend.
  - *Note: I have updated `vercel.json` to properly support React Client-Side Routing (SPA fallback to `index.html`).*
- **`backend/requirements.txt`**: Contains the Python dependencies (`Flask`, `pandas`, `pyarrow`, etc.). Vercel will automatically install these for the backend.
- **Parquet Files**: The transition to `.parquet` is fully supported on Vercel as `pyarrow` is included in your requirements.

## 🛠️ Deployment Steps

1. **Push your code to GitHub**: Make sure all your latest changes, including the updated `vercel.json`, are committed and pushed to your GitHub repository.
2. **Log into Vercel**: Go to your Vercel dashboard and click on **Add New...** -> **Project**.
3. **Import Repository**: Find your IPL Data Analysis repository in the list and click **Import**.
4. **Configure Project**:
   - **Project Name**: Choose a name (e.g., `ipl-data-analysis`).
   - **Framework Preset**: Leave it as **Other** (Vercel will rely on your `vercel.json`).
   - **Root Directory**: Leave it as `./` (the root of your repository).
   - **Build and Output Settings**: You don't need to change anything here. Your `vercel.json` overrides these settings.
   - **Environment Variables**: If you add any secret keys in the future, add them here. (None are required for the current version).
5. **Deploy**: Click the **Deploy** button.

Vercel will now build your frontend and prepare your serverless functions. This might take a couple of minutes.

## ⚠️ Troubleshooting

- **Serverless Function Size Limit**: Vercel has a 250MB limit (uncompressed) for Serverless Functions on the hobby tier. The `pandas` and `pyarrow` libraries are quite large.
  - *If your deployment fails during the build phase due to size limits*, you can switch out `pyarrow` for `fastparquet` in your `backend/requirements.txt`, and update `app.py` to use `engine='fastparquet'` when reading the parquet file. Usually, however, it fits just within the limit.
- **404 Errors on Frontend Navigation**: If you refresh the page on a route like `/players` and get a 404, ensure the `vercel.json` updates (which added the `filesystem` handle and `index.html` fallback) are deployed.

## 🏃‍♂️ Testing Locally

If you need to test the production build locally before deploying, you can use the Vercel CLI:
```bash
npm i -g vercel
vercel dev
```
This command emulates the Vercel deployment environment on your local machine.
