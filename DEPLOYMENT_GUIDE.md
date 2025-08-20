# Deployment Guide for Render

This guide will help you deploy your Django personal site to Render.

## Prerequisites

1. A Render account (free tier available)
2. Your code pushed to a GitHub repository
3. Supabase database credentials

## Deployment Steps

### 1. Prepare Your Repository

Make sure your repository contains:
- `requirements.txt` (updated with all dependencies)
- `build.sh` (build script for Render)
- `render.yaml` (optional, for infrastructure as code)

### 2. Create a Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `personal-site` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn personal_site.wsgi:application`

### 3. Set Environment Variables

In the Render dashboard, add these environment variables:

```
SECRET_KEY=your-secret-key-here
DEBUG=False
DATABASE_URL=your-supabase-database-url
ALLOWED_HOSTS=your-render-domain.onrender.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
OPENAI_API_KEY=your-openai-key
GROQ_API_KEY=your-groq-key
MNOTIFY_API_KEY=your-mnotify-key
ADMIN_PHONE_NUMBER=+233557782727
ADMIN_PASSWORD=your-admin-password
SITE_DOMAIN=https://your-render-domain.onrender.com
CLOUDINARY_CLOUD_NAME=your-cloudinary-cloud-name
CLOUDINARY_API_KEY=your-cloudinary-api-key
CLOUDINARY_API_SECRET=your-cloudinary-api-secret
```

### 4. Database Configuration

Your `DATABASE_URL` should be in this format:
```
postgresql://username:password@host:port/database
```

For Railway PostgreSQL, it looks like:
```
postgresql://postgres:FZidpyKPOFGwFhqTZSHMAHtaDnHaDAAT@metro.proxy.rlwy.net:11269/railway
```

### 5. Deploy

1. Click "Create Web Service"
2. Render will automatically build and deploy your application
3. Monitor the build logs for any errors

## Troubleshooting

### Common Issues

1. **Database Connection Errors**: 
   - Verify your `DATABASE_URL` is correct
   - Ensure Supabase allows connections from Render's IP ranges

2. **Static Files Not Loading**:
   - Make sure `whitenoise` is installed
   - Verify `STATIC_ROOT` and `STATICFILES_STORAGE` settings

3. **Build Failures**:
   - Check the build logs in Render dashboard
   - Ensure all dependencies are in `requirements.txt`

### Environment Variables

Make sure all required environment variables are set in Render:
- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to `False` for production
- `DATABASE_URL`: Your Supabase connection string
- `ALLOWED_HOSTS`: Your Render domain

### 5. Media Storage (Important!)

**Blog images disappearing?** This is because Render uses ephemeral storage.

Set up Cloudinary for persistent image storage:

1. Create free [Cloudinary account](https://cloudinary.com/)
2. Get your credentials from dashboard
3. Add to Render environment variables:
   ```
   CLOUDINARY_CLOUD_NAME=your-cloud-name
   CLOUDINARY_API_KEY=your-api-key
   CLOUDINARY_API_SECRET=your-api-secret
   ```
4. Test with: `python test_cloudinary_setup.py`

See `CLOUDINARY_SETUP_GUIDE.md` for detailed instructions.

## Post-Deployment

1. Run migrations: Your build script handles this automatically
2. Create a superuser: You may need to do this via Render's shell
3. Test all functionality including:
   - Portfolio pages
   - Blog functionality (upload images to test Cloudinary)
   - Newsletter subscription
   - Contact forms
   - RAG chatbot

## Security Notes

- Never commit sensitive data to your repository
- Use environment variables for all secrets
- Enable HTTPS (Render provides this automatically)
- Regularly update dependencies
