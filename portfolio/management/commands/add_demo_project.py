from django.core.management.base import BaseCommand
from portfolio.models import Project


class Command(BaseCommand):
    help = 'Add a demo project with live demo URL for testing'

    def handle(self, *args, **options):
        project_data = {
            'title': 'Newsletter System Demo',
            'description': '''A comprehensive newsletter subscription system built with Django. 
            
Features:
- User subscription with email validation
- Automated welcome emails
- Daily newsletter sending with curated content from Hacker News
- Admin dashboard for managing subscribers
- Email campaign tracking and analytics
- Responsive design with Bootstrap

This project demonstrates full-stack web development skills including backend API development, database design, email automation, and modern frontend design.''',
            'github_url': 'https://github.com/yourusername/newsletter-system',
            'live_demo_url': 'http://127.0.0.1:8000/newsletter/',
        }
        
        project, created = Project.objects.get_or_create(
            title=project_data['title'],
            defaults=project_data
        )
        
        if created:
            # Add some tags
            project.tags.add('Django', 'Python', 'Bootstrap', 'Email', 'Newsletter', 'Web Development')
            
            self.stdout.write(
                self.style.SUCCESS(f'Created demo project: {project.title}')
            )
            self.stdout.write(f'Live Demo URL: {project.live_demo_url}')
            self.stdout.write(f'GitHub URL: {project.github_url}')
        else:
            self.stdout.write(
                self.style.WARNING(f'Project already exists: {project.title}')
            )
