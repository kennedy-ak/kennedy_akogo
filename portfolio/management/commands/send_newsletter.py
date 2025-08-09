from django.core.management.base import BaseCommand
from portfolio.newsletter_utils import send_newsletter_to_all
from portfolio.models import NewsletterSubscriber


class Command(BaseCommand):
    help = 'Send newsletter to all active subscribers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending emails',
        )

    def handle(self, *args, **options):
        subscribers = NewsletterSubscriber.objects.filter(is_active=True)
        subscriber_count = subscribers.count()
        
        if subscriber_count == 0:
            self.stdout.write(
                self.style.WARNING('No active subscribers found.')
            )
            return
        
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would send newsletter to {subscriber_count} subscribers:')
            )
            for subscriber in subscribers:
                self.stdout.write(f'  - {subscriber.name} ({subscriber.email})')
            return
        
        self.stdout.write(f'Sending newsletter to {subscriber_count} subscribers...')
        
        success_count, total_count, campaign = send_newsletter_to_all()
        
        if success_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully sent {success_count} out of {total_count} emails!'
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR('Failed to send any emails. Check your email configuration.')
            )
