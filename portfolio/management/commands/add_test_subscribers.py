from django.core.management.base import BaseCommand
from portfolio.models import NewsletterSubscriber


class Command(BaseCommand):
    help = 'Add test subscribers for newsletter testing'

    def handle(self, *args, **options):
        test_subscribers = [
            {
                'name': 'Kennedy Akogo',
                'email': 'kennedyakogokweku@gmail.com',
                'phone': '+233557782727'
            },
            {
                'name': 'Test User 1',
                'email': 'test1@example.com',
                'phone': '+1234567890'
            },
            {
                'name': 'Test User 2', 
                'email': 'test2@example.com',
                'phone': ''
            }
        ]
        
        created_count = 0
        for subscriber_data in test_subscribers:
            subscriber, created = NewsletterSubscriber.objects.get_or_create(
                email=subscriber_data['email'],
                defaults={
                    'name': subscriber_data['name'],
                    'phone': subscriber_data['phone'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created subscriber: {subscriber.name} ({subscriber.email})')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Subscriber already exists: {subscriber.name} ({subscriber.email})')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Added {created_count} new test subscribers.')
        )
