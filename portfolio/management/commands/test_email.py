from django.core.management.base import BaseCommand
from portfolio.newsletter_utils import send_test_email, send_email


class Command(BaseCommand):
    help = 'Test email sending functionality'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email address to send test to')
        parser.add_argument(
            '--simple',
            action='store_true',
            help='Send a simple test email instead of newsletter format',
        )

    def handle(self, *args, **options):
        email = options['email']
        
        if options['simple']:
            # Send simple test email
            subject = "Simple Test Email"
            message = "This is a simple test email to verify email sending is working."
            success = send_email(email, subject, message)
        else:
            # Send newsletter format test email
            success = send_test_email(email)
        
        if success:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully sent test email to {email}')
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'Failed to send test email to {email}')
            )
