# MongoDB Setup Guide for Django Personal Site

## Why MongoDB?

MongoDB is a great alternative to PostgreSQL for your Django project because:

- **No connection issues**: More reliable than the Supabase connection problems
- **Flexible schema**: Perfect for evolving project requirements
- **Free tier**: MongoDB Atlas offers generous free tier
- **Easy deployment**: Works well with Render and other platforms
- **JSON-native**: Great for storing RAG embeddings and complex data

## Setup Steps

### 1. Create MongoDB Atlas Account

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Sign up for a free account
3. Create a new project (e.g., "Personal Site")
4. Create a free cluster (M0 Sandbox - 512 MB storage)

### 2. Configure Database Access

1. **Database Access**: Create a database user
   - Username: `personal_site_user` (or your choice)
   - Password: Generate a secure password
   - Database User Privileges: `Read and write to any database`

2. **Network Access**: Add IP addresses
   - Add your current IP: `Add Current IP Address`
   - For deployment: Add `0.0.0.0/0` (allow access from anywhere)
   - Or add specific Render IP ranges

### 3. Get Connection String

1. Click "Connect" on your cluster
2. Choose "Connect your application"
3. Select "Python" and version "3.6 or later"
4. Copy the connection string:
   ```
   mongodb+srv://personal_site_user:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

### 4. Install Required Packages

```bash
pip install djongo pymongo dnspython
```

### 5. Update Environment Variables

Update your `.env` file:
```bash
# MongoDB Atlas Database
MONGODB_URI=mongodb+srv://personal_site_user:your-password@cluster0.xxxxx.mongodb.net/personal_site?retryWrites=true&w=majority
```

### 6. Test Connection

```bash
python test_mongodb_connection.py
```

### 7. Run Migrations

```bash
python manage.py migrate
```

### 8. Create Superuser

```bash
python manage.py createsuperuser
```

## Configuration Details

### Django Settings

Your `settings.py` now uses:

```python
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/personal_site')

DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'personal_site',
        'CLIENT': {
            'host': MONGODB_URI,
        }
    }
}
```

### Model Compatibility

Your existing models are compatible with MongoDB through Djongo:

- ✅ **Basic fields**: CharField, TextField, EmailField, etc.
- ✅ **DateTime fields**: DateTimeField, auto_now, auto_now_add
- ✅ **Boolean fields**: BooleanField
- ✅ **Relationships**: ForeignKey, OneToOneField
- ✅ **Rich text**: CKEditor fields
- ⚠️ **Tags**: django-taggit works but may need special handling

### RAG System Benefits

MongoDB is actually better for your RAG system:

1. **Native JSON storage**: Perfect for embeddings and chunks
2. **Flexible schema**: Easy to add new RAG features
3. **Vector search**: MongoDB Atlas supports vector search (future upgrade)
4. **Large documents**: Better for storing repository content

## Deployment on Render

### Environment Variables

Add to your Render service:

```bash
MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/personal_site?retryWrites=true&w=majority
```

### Build Script

Your `build.sh` remains the same:

```bash
#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
```

## Advantages Over PostgreSQL

### 1. Reliability
- No DNS resolution issues
- More stable connections
- Better error handling

### 2. Flexibility
- Schema-less design
- Easy to add new fields
- Perfect for evolving requirements

### 3. Performance
- Fast for read-heavy applications
- Good for storing large documents (RAG content)
- Built-in caching

### 4. Development Experience
- Easier local development
- Better debugging tools
- More intuitive for JSON data

## Migration from PostgreSQL

If you have existing data in PostgreSQL:

1. **Export data**: Use Django fixtures
   ```bash
   python manage.py dumpdata > data.json
   ```

2. **Switch to MongoDB**: Update settings and migrate

3. **Import data**: Load fixtures
   ```bash
   python manage.py loaddata data.json
   ```

## Troubleshooting

### Common Issues

1. **Connection timeout**
   - Check IP whitelist in MongoDB Atlas
   - Verify connection string format
   - Test with `test_mongodb_connection.py`

2. **Authentication failed**
   - Verify username and password
   - Check database user permissions
   - Ensure user has access to the database

3. **Migration errors**
   - Some complex queries might need adjustment
   - Check Djongo documentation for specific issues

### Getting Help

- [Djongo Documentation](https://djongo.readthedocs.io/)
- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com/)
- [PyMongo Documentation](https://pymongo.readthedocs.io/)

## Next Steps

1. **Set up MongoDB Atlas account**
2. **Install packages**: `pip install djongo pymongo dnspython`
3. **Update `.env` with your MongoDB URI**
4. **Test connection**: `python test_mongodb_connection.py`
5. **Run migrations**: `python manage.py migrate`
6. **Deploy to Render** with new environment variables

MongoDB will solve your database connection issues and provide a more flexible foundation for your personal site!
