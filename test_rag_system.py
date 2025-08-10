#!/usr/bin/env python
"""
Test script to debug the RAG system with OpenAI embeddings
"""

import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'personal_site.settings')
django.setup()

from portfolio.models import Project, ProjectRAG
from portfolio.rag_service import RAGService
from django.core.management.color import make_style

style = make_style()

def test_rag_system():
    print(style.HTTP_INFO("🔍 RAG System Debug"))
    print("=" * 50)
    
    # 1. Check API keys
    print(style.HTTP_INFO("🔑 API Key Configuration:"))
    openai_key = getattr(settings, 'OPENAI_API_KEY', '')
    groq_key = getattr(settings, 'GROQ_API_KEY', '')
    
    print(f"OPENAI_API_KEY: {'SET' if openai_key else 'NOT SET'}")
    print(f"GROQ_API_KEY: {'SET' if groq_key else 'NOT SET'}")
    
    if not openai_key:
        print(style.ERROR("❌ OPENAI_API_KEY is required for embeddings!"))
        print(style.WARNING("Add OPENAI_API_KEY=your-api-key to your .env file"))
        return False
    
    if not groq_key:
        print(style.ERROR("❌ GROQ_API_KEY is required for chat responses!"))
        return False
    
    print()
    
    # 2. Check projects with GitHub URLs
    print(style.HTTP_INFO("📂 Projects with GitHub URLs:"))
    projects_with_github = Project.objects.filter(github_url__isnull=False).exclude(github_url='')
    print(f"Found {projects_with_github.count()} projects with GitHub URLs")
    
    if projects_with_github.count() == 0:
        print(style.ERROR("❌ No projects with GitHub URLs found!"))
        return False
    
    for project in projects_with_github[:3]:  # Show first 3
        print(f"- {project.title}: {project.github_url}")
    print()
    
    # 3. Test RAG service initialization
    print(style.HTTP_INFO("🤖 Testing RAG Service:"))
    try:
        rag_service = RAGService()
        
        if not rag_service.openai_client:
            print(style.ERROR("❌ OpenAI client not initialized!"))
            return False
        else:
            print(style.SUCCESS("✅ OpenAI client initialized"))
        
        if not rag_service.groq_client:
            print(style.ERROR("❌ Groq client not initialized!"))
            return False
        else:
            print(style.SUCCESS("✅ Groq client initialized"))
        
    except Exception as e:
        print(style.ERROR(f"❌ Error initializing RAG service: {e}"))
        return False
    
    print()
    
    # 4. Test with a specific project
    print(style.HTTP_INFO("🧪 Testing with a Project:"))
    test_project = projects_with_github.first()
    print(f"Testing with: {test_project.title}")
    
    try:
        # Check if project has RAG data
        rag_data, created = ProjectRAG.objects.get_or_create(project=test_project)
        
        if not rag_data.is_processed or not rag_data.embeddings_data:
            print(style.WARNING("⚠️ Project not processed yet. Processing..."))
            
            # Try to process the project
            success = rag_service.process_project_repository(test_project)
            
            if success:
                print(style.SUCCESS("✅ Project processed successfully!"))
            else:
                print(style.ERROR("❌ Failed to process project"))
                return False
        else:
            print(style.SUCCESS("✅ Project already processed"))
        
        # Test a simple query
        print(style.HTTP_INFO("💬 Testing Query:"))
        test_query = "What is this project about?"
        print(f"Query: {test_query}")
        
        response = rag_service.generate_response_with_groq(
            user_message=test_query,
            context_chunks=[],
            project_title=test_project.title,
            chat_history=[]
        )
        
        if response and "Sorry, there was an issue" not in response:
            print(style.SUCCESS(f"✅ Response: {response[:100]}..."))
            return True
        else:
            print(style.ERROR(f"❌ Poor response: {response}"))
            return False
            
    except Exception as e:
        print(style.ERROR(f"❌ Error testing project: {e}"))
        import traceback
        traceback.print_exc()
        return False

def show_setup_instructions():
    print(style.HTTP_INFO("\n📋 Setup Instructions:"))
    print("=" * 50)
    print("1. Get OpenAI API Key:")
    print("   - Go to https://platform.openai.com/api-keys")
    print("   - Create a new API key")
    print("   - Add to .env: OPENAI_API_KEY=your-key-here")
    print()
    print("2. Make sure you have projects with GitHub URLs")
    print("3. Process projects by visiting the chatbot page")
    print("4. Test queries on the project chatbot")

if __name__ == "__main__":
    print(style.HTTP_INFO("🚀 RAG System Test"))
    print("=" * 50)
    
    success = test_rag_system()
    
    if success:
        print(style.SUCCESS("\n🎉 RAG system is working with OpenAI!"))
    else:
        print(style.ERROR("\n💥 RAG system has issues!"))
        show_setup_instructions()
