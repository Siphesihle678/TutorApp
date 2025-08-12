# Online Learning Platform - Deployment Guide

## Overview

This guide will help you deploy the Online Learning Platform to Railway, making it accessible on the internet.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Account**: For version control
3. **PostgreSQL Database**: Railway provides this

## Step 1: Prepare Your Repository

1. Initialize Git repository (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. Create a GitHub repository and push your code:
   ```bash
   git remote add origin https://github.com/yourusername/online-learning-platform.git
   git push -u origin main
   ```

## Step 2: Deploy to Railway

### Option A: Deploy via Railway Dashboard

1. Go to [railway.app](https://railway.app) and sign in
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will automatically detect the Python project and deploy it

### Option B: Deploy via Railway CLI

1. Install Railway CLI:
   ```bash
   npm install -g @railway/cli
   ```

2. Login to Railway:
   ```bash
   railway login
   ```

3. Initialize and deploy:
   ```bash
   railway init
   railway up
   ```

## Step 3: Configure Environment Variables

In your Railway project dashboard, add these environment variables:

### Required Variables
```
DATABASE_URL=postgresql://username:password@host:port/database
SECRET_KEY=your-super-secret-key-here
```

### Optional Variables (for email functionality)
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourdomain.com
```

### Database Setup
1. In Railway dashboard, add a PostgreSQL service
2. Copy the connection string and set it as `DATABASE_URL`
3. The database tables will be created automatically on first run

## Step 4: Configure Frontend

1. Update the API base URL in frontend files:
   - Open `frontend/index.html`
   - Change `const API_BASE_URL = 'http://localhost:8000/api';` to your Railway URL
   - Example: `const API_BASE_URL = 'https://your-app.railway.app/api';`

2. Do the same for:
   - `frontend/teacher/dashboard.html`
   - `frontend/student/dashboard.html`

## Step 5: Deploy Frontend

### Option A: Deploy to Railway Static Site
1. In Railway dashboard, add a new service
2. Choose "Static Site"
3. Point to your `frontend` directory
4. Set build command: `echo "Static site"`
5. Set output directory: `.`

### Option B: Deploy to Netlify/Vercel
1. Push your frontend code to a separate repository
2. Connect to Netlify or Vercel
3. Set build settings to serve static files

## Step 6: Test Your Deployment

1. Visit your Railway app URL
2. Register a teacher account
3. Register a student account
4. Test the basic functionality:
   - Login/logout
   - Create a quiz (teacher)
   - Take a quiz (student)
   - View performance data

## Step 7: Custom Domain (Optional)

1. In Railway dashboard, go to your project settings
2. Add a custom domain
3. Configure DNS records as instructed

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify `DATABASE_URL` is correct
   - Check if PostgreSQL service is running

2. **CORS Errors**
   - Update CORS settings in `main.py` to include your frontend domain
   - Add your domain to `allow_origins` list

3. **Email Not Working**
   - Verify SMTP credentials
   - For Gmail, use App Passwords instead of regular password

4. **Build Failures**
   - Check Railway logs for specific error messages
   - Verify all dependencies are in `requirements.txt`

### Logs and Monitoring

1. View logs in Railway dashboard
2. Monitor application health at `/health` endpoint
3. Check database connections and performance

## Security Considerations

1. **Environment Variables**: Never commit sensitive data to Git
2. **HTTPS**: Railway provides SSL certificates automatically
3. **Database**: Use strong passwords and restrict access
4. **API Keys**: Rotate keys regularly

## Scaling

1. **Auto-scaling**: Railway can automatically scale based on traffic
2. **Database**: Upgrade to higher tier for better performance
3. **CDN**: Consider using a CDN for static assets

## Maintenance

1. **Updates**: Regularly update dependencies
2. **Backups**: Railway provides automatic database backups
3. **Monitoring**: Set up alerts for downtime or errors

## Support

- Railway Documentation: [docs.railway.app](https://docs.railway.app)
- FastAPI Documentation: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- PostgreSQL Documentation: [postgresql.org/docs](https://www.postgresql.org/docs)

## Example Environment Variables

```env
# Database
DATABASE_URL=postgresql://postgres:password@containers-us-west-1.railway.app:5432/railway

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production

# Email (Gmail example)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourdomain.com

# Application
DEBUG=False
```

## Quick Start Commands

```bash
# Clone and setup
git clone https://github.com/yourusername/online-learning-platform.git
cd online-learning-platform

# Deploy to Railway
railway login
railway init
railway up

# View logs
railway logs

# Open in browser
railway open
```

Your Online Learning Platform should now be live and accessible on the internet! 🎉
