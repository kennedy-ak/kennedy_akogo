from celery import shared_task
from django.db import transaction
import logging
import json
import numpy as np
from .models import Project, ProjectRAG
from .rag_service import ProjectRAGService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_project_rag_async(self, project_id, force=False):
    """
    Async task to process RAG data for a project
    """
    try:
        project = Project.objects.get(id=project_id)
        logger.info(f'Starting RAG processing for project: {project.title}')
        
        # Get or create ProjectRAG instance
        project_rag, created = ProjectRAG.objects.get_or_create(
            project=project,
            defaults={
                'repo_content': '',
                'embeddings_data': '',
                'is_processed': False,
                'processing_status': 'pending'
            }
        )
        
        # Skip if already processed and not forcing
        if project_rag.is_processed and not force:
            return f'Skipping {project.title} - already processed'
        
        # Initialize RAG service
        rag_service = ProjectRAGService()
        
        # Update status to fetching
        project_rag.processing_status = 'fetching'
        project_rag.progress_percentage = 10
        project_rag.processing_error = None
        project_rag.save()
        
        # Fetch repository content asynchronously
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            repo_content = loop.run_until_complete(
                rag_service.fetch_repo_content_async(project.github_url, timeout=30)
            )
        finally:
            loop.close()
        
        if not repo_content:
            error_msg = 'Failed to fetch repository content'
            project_rag.processing_error = error_msg
            project_rag.processing_status = 'failed'
            project_rag.save()
            raise Exception(error_msg)
        
        # Store raw content and update status
        project_rag.repo_content = repo_content
        project_rag.processing_status = 'chunking'
        project_rag.progress_percentage = 30
        project_rag.save()
        
        # Chunk the content
        chunks = rag_service.chunk_text(repo_content)
        
        if not chunks:
            error_msg = 'No content chunks generated'
            project_rag.processing_error = error_msg
            project_rag.processing_status = 'failed'
            project_rag.save()
            raise Exception(error_msg)
        
        # Update status to embedding
        project_rag.processing_status = 'embedding'
        project_rag.progress_percentage = 50
        project_rag.save()
        
        # Create embeddings
        embeddings, faiss_index = rag_service.create_embeddings(chunks)
        
        if embeddings is None or faiss_index is None:
            error_msg = 'Failed to create embeddings'
            project_rag.processing_error = error_msg
            project_rag.processing_status = 'failed'
            project_rag.save()
            raise Exception(error_msg)
        
        # Serialize embeddings data
        embeddings_data = {
            'chunks': chunks,
            'embeddings': embeddings.tolist(),
            'embedding_dimension': embeddings.shape[1],
            'num_chunks': len(chunks)
        }
        
        # Store embeddings data and mark as completed
        project_rag.set_embeddings_data(embeddings_data)
        project_rag.is_processed = True
        project_rag.processing_status = 'completed'
        project_rag.progress_percentage = 100
        
        with transaction.atomic():
            project_rag.save()
        
        logger.info(f'Successfully processed RAG data for {project.title}')
        return f'Successfully processed {project.title}'
        
    except Project.DoesNotExist:
        error_msg = f'Project with ID {project_id} not found'
        logger.error(error_msg)
        raise Exception(error_msg)
        
    except Exception as exc:
        error_msg = f'Error processing project {project_id}: {str(exc)}'
        logger.error(error_msg, exc_info=True)
        
        # Update error state if possible
        try:
            if 'project_rag' in locals():
                project_rag.processing_error = error_msg
                project_rag.processing_status = 'failed'
                project_rag.save()
        except Exception:
            pass
        
        # Retry the task
        if self.request.retries < self.max_retries:
            logger.info(f'Retrying task in 60 seconds (attempt {self.request.retries + 1})')
            raise self.retry(countdown=60, exc=exc)
        
        raise Exception(error_msg)


@shared_task
def batch_process_rag_projects():
    """
    Process all pending RAG projects
    """
    pending_projects = Project.objects.filter(
        github_url__isnull=False,
        rag_data__processing_status__in=['pending', 'failed']
    ).exclude(github_url='')
    
    results = []
    for project in pending_projects:
        task_result = process_project_rag_async.delay(project.id)
        results.append(f'Queued task {task_result.id} for project {project.title}')
    
    return results


@shared_task(bind=True)
def cleanup_failed_rag_tasks(self):
    """
    Clean up failed RAG processing tasks
    """
    failed_rags = ProjectRAG.objects.filter(processing_status='failed')
    count = 0
    
    for rag in failed_rags:
        # Reset to pending to allow retry
        rag.processing_status = 'pending'
        rag.progress_percentage = 0
        rag.processing_error = None
        rag.save()
        count += 1
    
    return f'Reset {count} failed RAG processing tasks'