# Deployment Guide for Lea James Recipe Calculator

This guide covers deploying the application to Railway and setting up GitHub for collaboration.

## Prerequisites

1. [Railway account](https://railway.app)
2. [GitHub account](https://github.com)
3. Git installed locally

## Step 1: Push to GitHub

1. Create a new repository on GitHub:
   - Go to https://github.com/new
   - Name: `lea-james-recipe-calculator` (or your preferred name)
   - Keep it private initially
   - Don't initialize with README (we already have files)

2. Push your local code:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/lea-james-recipe-calculator.git
   git branch -M main
   git push -u origin main
   ```

## Step 2: Deploy to Railway

### Option A: Deploy from GitHub (Recommended)

1. Log in to [Railway](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account if not already connected
5. Select your repository
6. Railway will auto-detect the Flask app and start deployment

### Option B: Deploy via CLI

1. Install Railway CLI:
   ```bash
   npm install -g @railway/cli
   ```

2. Login and deploy:
   ```bash
   railway login
   railway init
   railway up
   ```

## Step 3: Configure Production Settings

In Railway dashboard:

1. Go to your project settings
2. Add environment variables:
   - `FLASK_ENV`: `production`
   - `DATABASE_URL`: Railway will provide this for PostgreSQL (optional)

3. If you want to keep using SQLite:
   - Create a volume in Railway for persistent storage
   - Mount it to `/data`
   - Update `app.py` to use `/data/restaurant_calculator.db`

## Step 4: Database Considerations

### For SQLite (Simple, good for small deployments):
- Works out of the box
- Need to configure Railway volume for persistence
- Limited to single server

### For PostgreSQL (Recommended for production):
1. Add PostgreSQL service in Railway
2. Update your app to support PostgreSQL:
   ```python
   import os
   DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///restaurant_calculator.db')
   ```

## Collaboration Benefits

With GitHub + Railway setup:

1. **Multiple Developers**: 
   - Designers can clone the repo and work on UI/UX
   - You can review changes via Pull Requests
   - Railway auto-deploys when you merge to main

2. **Version Control**:
   - Track all changes
   - Revert if needed
   - See who changed what

3. **Branching**:
   - Create feature branches for new work
   - Test in Railway preview environments
   - Merge when ready

## Working with Designers

1. Give them repository access on GitHub
2. They can work on:
   - `/static/css/` - Stylesheets
   - `/static/js/` - JavaScript enhancements
   - `/static/images/` - Icons and images
   - `/templates/` - HTML structure

3. Recommended workflow:
   - Designer creates a branch: `git checkout -b improve-ui`
   - Makes changes and commits
   - Opens Pull Request
   - You review and merge

## Custom Domain

In Railway:
1. Go to Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed

## Monitoring

Railway provides:
- Logs viewer
- Metrics dashboard
- Deployment history
- Crash notifications

## Next Steps

1. Set up staging environment (separate Railway project)
2. Configure automated backups for database
3. Set up monitoring alerts
4. Consider adding:
   - User authentication
   - SSL certificate (Railway provides free)
   - CDN for static assets

## Useful Commands

```bash
# View logs
railway logs

# Run commands in production
railway run python manage.py

# Open production site
railway open
```

## Support

- Railway Discord: https://discord.gg/railway
- Railway Docs: https://docs.railway.app
- GitHub Docs: https://docs.github.com