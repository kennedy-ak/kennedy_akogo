from django.core.management.base import BaseCommand
from django.db import transaction
from portfolio.models import Project, ProjectRAG
from portfolio.rag_service import ProjectRAGService
import json
import numpy as np
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Process RAG data for projects with GitHub URLs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--project-id',
            type=int,
            help='Process specific project by ID',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reprocessing even if already processed',
        )

    def handle(self, *args, **options):
        rag_service = ProjectRAGService()
        
        if options['project_id']:
            # Process specific project
            try:
                project = Project.objects.get(id=options['project_id'])
                self.process_project(project, rag_service, options['force'])
            except Project.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Project with ID {options["project_id"]} not found')
                )
        else:
            # Process all projects with GitHub URLs
            projects = Project.objects.filter(github_url__isnull=False).exclude(github_url='')
            
            self.stdout.write(f'Found {projects.count()} projects with GitHub URLs')
            
            for project in projects:
                self.process_project(project, rag_service, options['force'])

    def process_project(self, project, rag_service, force=False):
        """Process RAG data for a single project"""
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
            
            # Skip if already processed and not forcing
            if project_rag.is_processed and not force:
                self.stdout.write(
                    self.style.WARNING(f'  Skipping {project.title} - already processed')
                )
                return
            
            # Reset processing state
            project_rag.is_processed = False
            project_rag.processing_error = None
            project_rag.save()
            
            # Fetch repository content using Gitingest
            self.stdout.write(f'  Fetching repository content from: {project.github_url}')
            repo_content = rag_service.fetch_repo_content_with_gitingest(project.github_url)
            
            if not repo_content:
                error_msg = 'Failed to fetch repository content'
                project_rag.processing_error = error_msg
                project_rag.save()
                self.stdout.write(self.style.ERROR(f'  {error_msg}'))
                return
            
            # Store raw content
            project_rag.repo_content = repo_content
            
            # Chunk the content
            self.stdout.write('  Chunking repository content...')
            chunks = rag_service.chunk_text(repo_content)
            
            if not chunks:
                error_msg = 'No content chunks generated'
                project_rag.processing_error = error_msg
                project_rag.save()
                self.stdout.write(self.style.ERROR(f'  {error_msg}'))
                return
            
            self.stdout.write(f'  Generated {len(chunks)} chunks')
            
            # Create embeddings
            self.stdout.write('  Creating embeddings...')
            embeddings, faiss_index = rag_service.create_embeddings(chunks)
            
            if embeddings.size == 0 or faiss_index is None:
                error_msg = 'Failed to create embeddings'
                project_rag.processing_error = error_msg
                project_rag.save()
                self.stdout.write(self.style.ERROR(f'  {error_msg}'))
                return
            
            # Serialize embeddings data
            embeddings_data = {
                'chunks': chunks,
                'embeddings': embeddings.tolist(),  # Convert numpy array to list for JSON
                'embedding_dimension': embeddings.shape[1] if embeddings.size > 0 else 0,
                'num_chunks': len(chunks)
            }
            
            # Store embeddings data
            project_rag.set_embeddings_data(embeddings_data)
            project_rag.is_processed = True
            
            # Final check that project still exists before saving
            if not Project.objects.filter(id=project.id).exists():
                self.stdout.write(
                    self.style.ERROR(f'Project {project.id} was deleted during processing')
                )
                return
            
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
                # Check if project still exists before updating ProjectRAG
                if Project.objects.filter(id=project.id).exists():
                    project_rag.processing_error = error_msg
                    project_rag.is_processed = False
                    project_rag.save()
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Project {project.id} was deleted, skipping error update')
                    )
            except Exception as save_error:
                logger.error(f'Failed to save error state: {save_error}')
                pass
            
            self.stdout.write(self.style.ERROR(f'  {error_msg}'))
