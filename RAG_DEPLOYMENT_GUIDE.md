# RAG System Deployment Guide for Render

## Problem: Timeout Issues on Render

Your RAG feature times out on Render because:

1. **Synchronous Processing**: RAG processing happens during HTTP requests
2. **Resource Intensive**: Creating embeddings for large repositories takes time
3. **API Rate Limits**: Sequential OpenAI API calls are slow
4. **Memory Constraints**: Render's free tier has limited resources

## Solution: Asynchronous Processing

**Multithreading won't solve this** - it could make resource constraints worse. Instead, use asynchronous background processing.

## Implementation Changes Made

### 1. Optimized Embedding Creation
- **Batch Processing**: Process multiple chunks in single API calls
- **Reduced File Size**: Lowered max file size from 100KB to 50KB
- **Shorter Timeouts**: Reduced API timeouts to fail faster

### 2. Added Processing Status Tracking
- **Status Fields**: `processing_status` and `progress_percentage`
- **Better UX**: Users see processing progress instead of timeouts
- **Error Handling**: Failed processing is tracked and displayed

### 3. Async Management Command
- **Resource Management**: Batching with delays between API calls
- **Progress Tracking**: Updates status throughout processing
- **Error Recovery**: Handles failures gracefully

## Deployment Options

### Option 1: Manual Processing (Recommended for Render Free Tier)

1. **Remove Automatic Processing**: Users see "Initialize AI" button
2. **Manual Trigger**: Admin runs processing command manually
3. **Status Updates**: Users see processing progress

```bash
# Process specific project
python manage.py process_rag_async --project-id=1

# Process all pending projects
python manage.py process_rag_async

# With custom settings
python manage.py process_rag_async --batch-size=25 --delay=2.0
```

### Option 2: Scheduled Processing (If you upgrade Render plan)

1. **Cron Jobs**: Use Render's cron jobs feature
2. **Background Workers**: Run processing in separate worker dyno
3. **Queue System**: Add Redis + Celery for proper job queuing

## Render Configuration

### Environment Variables
Add these to your Render service:

```bash
# Existing variables
OPENAI_API_KEY=your-openai-key
GROQ_API_KEY=your-groq-key

# Optional: Reduce resource usage
RAG_BATCH_SIZE=25
RAG_DELAY=1.5
RAG_TIMEOUT=20
```

### Build Script Update
Update your `build.sh`:

```bash
#!/usr/bin/env bash
set -o errexit

echo "🚀 Starting build process..."

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate

# Optional: Process any pending RAG data (be careful with timeouts)
# python manage.py process_rag_async --batch-size=10 --delay=3.0

echo "✅ Build completed successfully!"
```

## Usage Instructions

### For Users
1. Visit project detail page
2. See AI assistant status (Pending/Processing/Ready/Failed)
3. Click "Initialize AI" to start processing (if pending)
4. Wait for processing to complete
5. Use "Start Conversation" when ready

### For Admins
1. **Monitor Processing**: Check Django admin for ProjectRAG status
2. **Manual Processing**: Run management command when needed
3. **Troubleshooting**: Check processing_error field for failures

```bash
# Check status of all projects
python manage.py shell
>>> from portfolio.models import ProjectRAG
>>> for rag in ProjectRAG.objects.all():
...     print(f"{rag.project.title}: {rag.processing_status} ({rag.progress_percentage}%)")
```

## Performance Optimizations

### 1. Resource Management
- **Batch Size**: Process 25-50 chunks per API call
- **Delays**: 1-2 second delays between batches
- **Timeouts**: 20-30 second API timeouts

### 2. Content Filtering
- **File Size Limit**: 50KB max per file
- **Exclude Patterns**: Skip docs, images, binaries
- **Smart Chunking**: 1000 chars with 200 char overlap

### 3. Error Handling
- **Graceful Failures**: Continue processing other projects
- **Status Tracking**: Clear error messages for users
- **Retry Logic**: Manual retry for failed projects

## Monitoring and Maintenance

### 1. Regular Checks
```bash
# Check for failed processing
python manage.py shell
>>> ProjectRAG.objects.filter(processing_status='failed').count()

# Retry failed projects
python manage.py process_rag_async
```

### 2. Performance Metrics
- **Processing Time**: Monitor how long each project takes
- **Success Rate**: Track failed vs successful processing
- **Resource Usage**: Monitor memory and CPU during processing

### 3. Scaling Considerations
- **Upgrade Render Plan**: For automatic background processing
- **Add Redis**: For proper job queuing
- **Use Celery**: For distributed task processing

## Troubleshooting

### Common Issues

1. **Still Timing Out**
   - Reduce batch size: `--batch-size=10`
   - Increase delays: `--delay=3.0`
   - Process during low-traffic hours

2. **OpenAI Rate Limits**
   - Increase delays between batches
   - Use smaller batch sizes
   - Check your OpenAI usage limits

3. **Memory Issues**
   - Process one project at a time
   - Reduce max file size further
   - Clear processed data periodically

4. **Database Locks**
   - Add delays between projects
   - Use database transactions properly
   - Monitor connection pool usage

## Next Steps

1. **Test the Changes**: Deploy and test with a small project
2. **Monitor Performance**: Watch processing times and success rates
3. **Consider Upgrades**: If successful, consider Render paid plan for automation
4. **Add Monitoring**: Set up alerts for failed processing

The key insight is that **asynchronous processing with resource management** is the solution, not multithreading. This approach respects Render's constraints while providing a better user experience.
