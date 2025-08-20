from django.core.management.base import BaseCommand
from django.db import transaction
from portfolio.models import Project, ProjectRAG
from portfolio.rag_service import ProjectRAGService
import json
import numpy as np
import logging
import time

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Process RAG data asynchronously with better resource management'

    def add_arguments(self, parser):
        parser.add_argument(
            '--project-id',
            type=int,
            help='Process specific project by ID',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=50,
            help='Batch size for embedding processing',
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=1.0,
            help='Delay between batches in seconds',
        )

    def handle(self, *args, **options):
        rag_service = ProjectRAGService()
        
        if options['project_id']:
            # Process specific project
            try:
                project = Project.objects.get(id=options['project_id'])
                self.process_project_async(project, rag_service, options)
            except Project.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Project with ID {options["project_id"]} not found')
                )
        else:
            # Process all pending projects
            pending_projects = Project.objects.filter(
                github_url__isnull=False,
                rag_data__processing_status__in=['pending', 'failed']
            ).exclude(github_url='')
            
            self.stdout.write(f'Found {pending_projects.count()} projects to process')
            
            for project in pending_projects:
                self.process_project_async(project, rag_service, options)
                # Small delay between projects to avoid overwhelming the system
                time.sleep(2)

    def process_project_async(self, project, rag_service, options):
        """Process RAG data for a single project with better resource management"""
        self.stdout.write(f'Processing project: {project.title}')
        
        try:
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
            
            # Update status to fetching
            project_rag.processing_status = 'fetching'
            project_rag.progress_percentage = 10
            project_rag.processing_error = None
            project_rag.save()
            
            # Fetch repository content with shorter timeout
            self.stdout.write(f'  Fetching repository content from: {project.github_url}')
            repo_content = rag_service.fetch_repo_content_with_gitingest(
                project.github_url, timeout=20
            )
            
            if not repo_content:
                error_msg = 'Failed to fetch repository content'
                project_rag.processing_error = error_msg
                project_rag.processing_status = 'failed'
                project_rag.save()
                self.stdout.write(self.style.ERROR(f'  {error_msg}'))
                return
            
            # Store raw content and update status
            project_rag.repo_content = repo_content
            project_rag.processing_status = 'chunking'
            project_rag.progress_percentage = 30
            project_rag.save()
            
            # Chunk the content
            self.stdout.write('  Chunking repository content...')
            chunks = rag_service.chunk_text(repo_content)
            
            if not chunks:
                error_msg = 'No content chunks generated'
                project_rag.processing_error = error_msg
                project_rag.processing_status = 'failed'
                project_rag.save()
                self.stdout.write(self.style.ERROR(f'  {error_msg}'))
                return
            
            self.stdout.write(f'  Generated {len(chunks)} chunks')
            
            # Update status to embedding
            project_rag.processing_status = 'embedding'
            project_rag.progress_percentage = 50
            project_rag.save()
            
            # Create embeddings with batching and delays
            self.stdout.write('  Creating embeddings with resource management...')
            embeddings, faiss_index = self.create_embeddings_with_delays(
                rag_service, chunks, options['batch_size'], options['delay']
            )
            
            if embeddings is None or embeddings.size == 0 or faiss_index is None:
                error_msg = 'Failed to create embeddings'
                project_rag.processing_error = error_msg
                project_rag.processing_status = 'failed'
                project_rag.save()
                self.stdout.write(self.style.ERROR(f'  {error_msg}'))
                return
            
            # Serialize embeddings data
            embeddings_data = {
                'chunks': chunks,
                'embeddings': embeddings.tolist(),
                'embedding_dimension': embeddings.shape[1] if embeddings.size > 0 else 0,
                'num_chunks': len(chunks)
            }
            
            # Store embeddings data and mark as completed
            project_rag.set_embeddings_data(embeddings_data)
            project_rag.is_processed = True
            project_rag.processing_status = 'completed'
            project_rag.progress_percentage = 100
            
            with transaction.atomic():
                project_rag.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'  Successfully processed {project.title}')
            )
            
        except Exception as e:
            error_msg = f'Error processing project: {str(e)}'
            logger.error(error_msg, exc_info=True)
            
            # Update error state
            try:
                if Project.objects.filter(id=project.id).exists():
                    project_rag.processing_error = error_msg
                    project_rag.processing_status = 'failed'
                    project_rag.save()
            except Exception as save_error:
                logger.error(f'Failed to save error state: {save_error}')
            
            self.stdout.write(self.style.ERROR(f'  {error_msg}'))

    def create_embeddings_with_delays(self, rag_service, chunks, batch_size, delay):
        """Create embeddings with batching and delays to manage resources"""
        try:
            import numpy as np
            import faiss
            
            embeddings_list = []
            total_batches = (len(chunks) + batch_size - 1) // batch_size
            
            for i, batch_start in enumerate(range(0, len(chunks), batch_size)):
                batch_chunks = chunks[batch_start:batch_start + batch_size]
                
                self.stdout.write(f'    Processing batch {i+1}/{total_batches} ({len(batch_chunks)} chunks)')
                
                # Use the existing batch processing from rag_service
                response = rag_service.openai_client.embeddings.create(
                    model="text-embedding-3-small",
                    input=batch_chunks
                )
                
                # Extract embeddings from batch response
                for embedding_data in response.data:
                    embeddings_list.append(embedding_data.embedding)
                
                # Add delay between batches to avoid overwhelming the system
                if i < total_batches - 1:  # Don't delay after the last batch
                    time.sleep(delay)
            
            # Convert to numpy array
            embeddings = np.array(embeddings_list, dtype=np.float32)
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            
            # Create FAISS index
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatIP(dimension)
            index.add(embeddings)
            
            return embeddings, index
            
        except Exception as e:
            logger.error(f"Error creating embeddings with delays: {e}")
            return None, None
