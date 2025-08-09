import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
from django.conf import settings
from django.utils import timezone
from .models import NewsletterSubscriber, NewsletterCampaign


def get_top_article():
    """
    Fetch the top article from Hacker News
    """
    try:
        response = requests.get("https://news.ycombinator.com/news", timeout=10)
        yc_page = response.text
        soup = BeautifulSoup(yc_page, 'html.parser')
        
        articles = soup.find_all(name='span', class_='titleline')
        article_scores = soup.find_all(name='span', class_='score')
        
        if not articles or not article_scores:
            return "Unable to fetch top article", "https://news.ycombinator.com"
        
        all_articles = [article.getText() for article in articles]
        all_links = []
        
        for article in articles:
            link_element = article.find('a')
            if link_element:
                href = link_element.get("href")
                if href:
                    # Handle relative URLs
                    if href.startswith('item?'):
                        href = f"https://news.ycombinator.com/{href}"
                    elif not href.startswith('http'):
                        href = f"https://news.ycombinator.com/{href}"
                    all_links.append(href)
                else:
                    all_links.append("https://news.ycombinator.com")
            else:
                all_links.append("https://news.ycombinator.com")
        
        all_votes = []
        for score in article_scores:
            try:
                vote_text = score.getText().split()[0]
                all_votes.append(int(vote_text))
            except (ValueError, IndexError):
                all_votes.append(0)
        
        if all_votes:
            highest_index = all_votes.index(max(all_votes))
            return all_articles[highest_index], all_links[highest_index]
        else:
            return all_articles[0] if all_articles else "Unable to fetch top article", all_links[0] if all_links else "https://news.ycombinator.com"
            
    except Exception as e:
        print(f"Error fetching articles: {e}")
        return "Unable to fetch top article", "https://news.ycombinator.com"


def send_email(recipient, subject, message):
    """
    Send email using SMTP
    """
    try:
        sender_email = settings.EMAIL_HOST_USER
        password = settings.EMAIL_HOST_PASSWORD

        if not password:
            print("Email password not configured")
            return False

        email_message = MIMEMultipart()
        email_message["From"] = sender_email
        email_message["To"] = recipient
        email_message["Subject"] = subject

        email_message.attach(MIMEText(message, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.send_message(email_message)

        return True
    except Exception as e:
        print(f"Error sending email to {recipient}: {e}")
        return False


def send_welcome_email(subscriber):
    """
    Send welcome email to new subscriber
    """
    try:
        article_title, article_link = get_top_article()

        subject = "Welcome to Kennedy's Tech News Newsletter!"
        message = f"""Hi {subscriber.name},

Thank you for subscribing to my Tech News service! 🎉

You'll now receive daily updates on the latest tech trends directly in your inbox. I curate the most interesting and impactful stories from around the tech world to keep you informed and ahead of the curve.

🔥 Today's Featured Article:
{article_title}
Read more: {article_link}

What to expect:
-- Daily curated tech news from Hacker News
-- Latest innovations and breakthrough technologies
-- Insights on AI, machine learning, and emerging tech
-- Developer tools and programming trends

I'm excited to have you join my tech community! As a promise to you, I will constantly work to improve this service and provide even more value to subscribers like you.

If you have any feedback or suggestions, feel free to reply to this email.

Best regards,
Kennedy Akogo
AI/LLM Engineer 


"""

        return send_email(subscriber.email, subject, message)
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        return False


def send_newsletter_to_all():
    """
    Send newsletter to all active subscribers
    """
    try:
        subscribers = NewsletterSubscriber.objects.filter(is_active=True)
        article_title, article_link = get_top_article()
        
        subject = "Top Tech News Article"
        success_count = 0
        total_count = subscribers.count()
        
        # Create campaign record
        campaign = NewsletterCampaign.objects.create(
            title=f"Daily Newsletter - {timezone.now().strftime('%Y-%m-%d')}",
            subject=subject,
            content=f"Today's Top Tech article: {article_title}\nRead more at: {article_link}",
            article_title=article_title,
            article_link=article_link,
            total_sent=total_count
        )
        
        for subscriber in subscribers:
            personalized_message = f"""Hi {subscriber.name},

🔥 Today's Top Tech News

{article_title}

🔗 Read the full article: {article_link}

This article was selected based on community engagement and relevance from Hacker News, ensuring you get the most valuable tech content each day.

Stay curious and keep innovating!

Best regards,
Kennedy Akogo
AI/LLM Engineer

---
You're receiving this because you subscribed to Kennedy's Tech News Newsletter.

"""

            if send_email(subscriber.email, subject, personalized_message):
                success_count += 1
        
        # Update campaign with results
        campaign.success_count = success_count
        campaign.sent_at = timezone.now()
        campaign.save()
        
        return success_count, total_count, campaign
        
    except Exception as e:
        print(f"Error sending newsletter: {e}")
        return 0, 0, None


def send_test_email(test_email):
    """
    Send test newsletter to specified email
    """
    try:
        title, link = get_top_article()
        subject = "🧪 TEST - Kennedy's Tech News Newsletter"
        message = f"""Hi there,

This is a TEST email of Kennedy's Tech News newsletter.

🔥 Today's Featured Tech Article:
{title}

🔗 Read the full article: {link}

This is how your daily newsletter will look. The content is automatically curated from the top-voted articles on Hacker News.

If you received this test email, the newsletter system is working perfectly!

Best regards,
Kennedy Akogo
AI/LLM Engineer

---
This is a test email. If you're not expecting this, please ignore it.
"""
        return send_email(test_email, subject, message)
    except Exception as e:
        print(f"Error sending test email: {e}")
        return False
