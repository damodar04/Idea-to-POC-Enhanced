# Render Deployment Guide

This guide will help you deploy the Idea-to-POC-Enhanced application on Render.

## Prerequisites

1. A Render account (sign up at https://render.com)
2. A GitHub account with this repository
3. MongoDB Atlas cluster (or your MongoDB connection string)

## Step 1: Push Code to GitHub

If you haven't already, push your code to a GitHub repository:

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

## Step 2: Create a New Web Service on Render

1. Log in to your Render dashboard
2. Click **"New +"** button
3. Select **"Web Service"**
4. Connect your GitHub account if not already connected
5. Select the repository: `Idea-to-POC-Enhanced`
6. Select the branch: `main` (or your preferred branch)

## Step 3: Configure the Service

### Basic Settings

- **Name**: `idea-to-poc-enhanced` (or your preferred name)
- **Region**: Choose the closest region to your users
- **Branch**: `main`
- **Root Directory**: Leave empty (or set to root if needed)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`

### Environment Variables

Click on **"Environment"** tab and add the following environment variables:

#### MongoDB Configuration
```
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
MONGODB_DATABASE=i2poc
MONGODB_COLLECTION=ideas
```

#### API Keys
```
DEEPSEEK_API_KEY=your_deepseek_api_key_here
LANGSMITH_API_KEY=your_langsmith_api_key_here
GROQ_API_KEY=your_groq_api_key_here
GPT_4O_API_KEY=your_gpt4o_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-instance.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2025-01-01-preview
TAVILY_API_KEY=your_tavily_api_key_here
```

**Important**: 
- Make sure to mark sensitive values as **"Secret"** in Render
- Do NOT commit these values to your repository
- Render will automatically handle the `PORT` environment variable

## Step 4: Deploy

1. Click **"Create Web Service"**
2. Render will start building and deploying your application
3. Monitor the build logs for any errors
4. Once deployed, you'll get a URL like: `https://idea-to-poc-enhanced.onrender.com`

## Step 5: Verify Deployment

1. Visit your application URL
2. Test the login functionality
3. Verify MongoDB connection by submitting a test idea
4. Check the logs in Render dashboard for any errors

## Troubleshooting

### Build Fails

- Check that all dependencies in `requirements.txt` are valid
- Verify Python version compatibility (3.8+)
- Check build logs for specific error messages

### Application Won't Start

- Verify the start command is correct: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
- Check that all environment variables are set correctly
- Review application logs in Render dashboard

### MongoDB Connection Issues

**Common Issues and Solutions:**

1. **Connection Timeout**
   - The app now uses 30-second timeouts and automatic retry logic (3 attempts)
   - Check Render logs for connection attempts and errors
   - Verify your MongoDB Atlas cluster is running and accessible

2. **Network Access**
   - **CRITICAL**: MongoDB Atlas must allow connections from Render
   - In MongoDB Atlas Dashboard:
     - Go to **Network Access** → **IP Access List**
     - Click **"Add IP Address"**
     - Add `0.0.0.0/0` to allow all IPs (for testing)
     - Or add Render's specific IP ranges (more secure)
   - **Without this, your app cannot connect to MongoDB!**

3. **Connection String Format**
   - Ensure your `MONGODB_URL` is in the correct format:
     ```
     mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
     ```
   - The connection string should include:
     - `retryWrites=true`
     - `w=majority`
     - Your cluster name and credentials

4. **Authentication Issues**
   - Verify your MongoDB username and password are correct
   - Check if special characters in password are URL-encoded
   - Ensure the database user has read/write permissions

5. **Database/Collection Not Found**
   - MongoDB will create the database and collection automatically on first write
   - Verify `MONGODB_DATABASE` and `MONGODB_COLLECTION` environment variables are set

6. **Connection Pooling**
   - The app now uses connection pooling (5-50 connections)
   - This helps with performance and reliability on Render

**Testing Connection:**
- Check Render logs for connection status messages
- Look for "✅ MongoDB connection established successfully" in logs
- If you see connection errors, check the troubleshooting steps above

### Environment Variables Not Working

- Ensure all environment variables are set in Render dashboard
- Check that variable names match exactly (case-sensitive)
- Restart the service after adding new environment variables

## Using render.yaml (Alternative Method)

If you prefer to use the `render.yaml` file:

1. Ensure `render.yaml` is in your repository root
2. In Render dashboard, select **"Apply render.yaml"** when creating the service
3. Render will automatically configure the service based on the YAML file
4. You'll still need to add environment variables manually in the dashboard

## Auto-Deploy

By default, Render will auto-deploy when you push to the connected branch. To disable:

1. Go to your service settings
2. Under **"Auto-Deploy"**, select **"No"**

## Custom Domain

To use a custom domain:

1. Go to your service settings
2. Click **"Custom Domains"**
3. Add your domain
4. Follow the DNS configuration instructions

## Monitoring

- **Logs**: View real-time logs in the Render dashboard
- **Metrics**: Monitor CPU, memory, and request metrics
- **Alerts**: Set up alerts for service downtime

## Cost Considerations

- **Starter Plan**: Free tier available (with limitations)
- **Standard Plan**: $7/month per service
- **Pro Plan**: $25/month per service

Check Render's pricing page for current rates.

## Security Best Practices

1. ✅ Never commit API keys or secrets to the repository
2. ✅ Use Render's secret environment variables
3. ✅ Enable MongoDB authentication
4. ✅ Use HTTPS (automatically provided by Render)
5. ✅ Regularly rotate API keys
6. ✅ Monitor access logs

## Support

For issues:
- Check Render documentation: https://render.com/docs
- Review application logs in Render dashboard
- Check MongoDB Atlas connection logs

---

**Last Updated**: January 2025

