# Project RAG Chatbot Setup Guide

This guide will help you set up the project-specific RAG (Retrieval-Augmented Generation) chatbot feature that uses Gitingest to fetch GitHub repository content and creates an AI-powered discussion interface for each project.

## Overview

The RAG chatbot feature allows users to:
- Click "Discuss This Project" on any project with a GitHub URL
- Chat with an AI assistant that has knowledge of the project's codebase
- Ask questions about code, architecture, features, and implementation details
- Get contextual responses based on the actual repository content

## Prerequisites

1. **Python Environment**: Ensure you have Python 3.8+ installed
2. **Groq API Key**: Sign up at [Groq](https://console.groq.com/) and get your API key
3. **GitHub Repository**: Projects must have valid GitHub URLs

## Installation Steps

### 1. Install Required Dependencies

```bash
pip install sentence-transformers faiss-cpu groq numpy tiktoken
```

Or install from the updated requirements.txt:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Add the following to your `.env` file:

```env
# Groq API Configuration for RAG chatbot
GROQ_API_KEY=your-groq-api-key-here
```

You can get a free Groq API key from: https://console.groq.com/

### 3. Apply Database Migrations

The migrations have already been created and applied, but if you need to run them again:

```bash
python manage.py migrate
```

### 4. Process Project Repositories

Use the management command to fetch and process repository content for your projects:

```bash
# Process all projects with GitHub URLs
python manage.py process_project_rag

# Process a specific project by ID
python manage.py process_project_rag --project-id 1

# Force reprocessing (even if already processed)
python manage.py process_project_rag --force
```

## How It Works

### 1. Content Fetching
- Uses **Gitingest API** to fetch repository content as text
- Respects `.gitignore` rules and excludes binary files
- Handles public GitHub repositories automatically

### 2. Text Processing
- Splits repository content into overlapping chunks (1000 chars with 200 char overlap)
- Creates embeddings using `sentence-transformers` (all-MiniLM-L6-v2 model)
- Stores embeddings in **FAISS** vector database for fast similarity search

### 3. Query Processing
- User questions are embedded using the same model
- FAISS performs similarity search to find relevant code chunks
- Top 5 most relevant chunks are used as context

### 4. Response Generation
- **Groq** (llama3-8b-8192 model) generates responses using the relevant context
- Responses are contextual and specific to the project's codebase

## Usage

### For Users
1. Navigate to any project detail page that has a GitHub URL
2. Click the "Discuss This Project" button
3. Ask questions about the code, features, or implementation
4. Get AI-powered responses based on the actual repository content

### For Administrators
1. Access the Django admin panel
2. Go to "Project RAGs" to see processing status
3. Monitor which projects have been processed
4. View content previews and embeddings information

## Troubleshooting

### Common Issues

1. **"RAG dependencies not available"**
   - Install the required packages: `pip install sentence-transformers faiss-cpu groq numpy tiktoken`

2. **"Project repository is still being processed"**
   - Run the processing command: `python manage.py process_project_rag`
   - Check the admin panel for processing errors

3. **"Groq API error"**
   - Verify your GROQ_API_KEY is set correctly in the .env file
   - Check your Groq API quota and limits

4. **"Gitingest API error"**
   - Ensure the GitHub repository is public
   - Check if the GitHub URL is valid and accessible

### Processing Errors
Check the Django admin panel under "Project RAGs" to see detailed error messages for failed processing attempts.

## File Structure

```
portfolio/
├── models.py              # ProjectRAG model
├── rag_service.py         # RAG functionality
├── views.py               # Chatbot views
├── urls.py                # URL patterns
├── admin.py               # Admin interface
├── management/commands/
│   └── process_project_rag.py  # Processing command
└── templates/portfolio/
    └── project_chatbot.html    # Chatbot interface
```

## API Endpoints

- `GET /projects/<id>/discuss/` - Project chatbot page
- `POST /projects/<id>/discuss/ask/` - Send message to chatbot

## Security Notes

- Only public GitHub repositories are supported
- Repository content is cached locally for performance
- API keys should be kept secure and not committed to version control
- Consider rate limiting for production use

## Performance Considerations

- Initial processing can take 1-5 minutes per repository
- Embeddings are cached to avoid reprocessing
- FAISS provides fast similarity search even for large codebases
- Consider using background tasks (Celery) for processing in production

## Next Steps

1. Install the dependencies
2. Get your Groq API key
3. Add it to your .env file
4. Process your project repositories
5. Test the chatbot functionality

The feature is now ready to use! Users can discuss your projects with an AI that understands the actual codebase.
