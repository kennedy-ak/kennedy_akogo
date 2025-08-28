from django.db import models
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager
import json


class NewsletterSubscriber(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-subscribed_at']

    def __str__(self):
        return f"{self.name} - {self.email}"


class NewsletterCampaign(models.Model):
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    article_title = models.CharField(max_length=300, blank=True)
    article_link = models.URLField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    total_sent = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    tags = TaggableManager(help_text="A comma-separated list of tags.")
    github_url = models.URLField(blank=True, null=True, help_text="GitHub repository URL")
    live_demo_url = models.URLField(blank=True, null=True, help_text="Live demo/deployment URL")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_github_repo_name(self):
        """Extract repository name from GitHub URL"""
        if self.github_url:
            # Extract owner/repo from GitHub URL
            # e.g., https://github.com/owner/repo -> owner/repo
            parts = self.github_url.rstrip('/').split('/')
            if len(parts) >= 2:
                return f"{parts[-2]}/{parts[-1]}"
        return None


class ProjectRAG(models.Model):
    """Store RAG data for each project"""
    project = models.OneToOneField(Project, related_name='rag_data', on_delete=models.CASCADE)
    repo_content = models.TextField(blank=True, help_text="Raw repository content from Gitingest")
    embeddings_data = models.TextField(blank=True, help_text="JSON serialized embeddings and chunks")
    last_updated = models.DateTimeField(auto_now=True)
    is_processed = models.BooleanField(default=False)
    processing_error = models.TextField(blank=True, null=True)
    processing_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('fetching', 'Fetching Repository'),
            ('chunking', 'Processing Content'),
            ('embedding', 'Creating Embeddings'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='pending'
    )
    progress_percentage = models.IntegerField(default=0, help_text='Processing progress (0-100)')

    def __str__(self):
        return f"RAG data for {self.project.title}"

    def get_embeddings_data(self):
        """Deserialize embeddings data from JSON"""
        if self.embeddings_data:
            try:
                return json.loads(self.embeddings_data)
            except json.JSONDecodeError:
                return None
        return None

    def set_embeddings_data(self, data):
        """Serialize embeddings data to JSON"""
        self.embeddings_data = json.dumps(data)


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='project_images/')
    alt_text = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.project.title} - Image"


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = RichTextUploadingField()
    cover_image = models.ImageField(upload_to='blog_covers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_to_newsletter = models.BooleanField(default=False, help_text="Has this blog post been sent to newsletter subscribers?")

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_snippet(self, word_limit=50):
        """Generate a snippet of the blog post content"""
        from django.utils.html import strip_tags
        from django.utils.text import Truncator

        # Strip HTML tags and get plain text
        plain_text = strip_tags(self.content)

        # Truncate to specified word limit
        truncator = Truncator(plain_text)
        snippet = truncator.words(word_limit, truncate='...')

        return snippet

    def get_absolute_url(self):
        """Get the full URL for this blog post"""
        from django.urls import reverse
        from django.conf import settings

        relative_url = reverse('blog_detail', kwargs={'slug': self.slug})

        # Get the domain from settings or use a default
        domain = getattr(settings, 'SITE_DOMAIN', 'http://127.0.0.1:8000')
        return f"{domain}{relative_url}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Message from {self.name} - {self.created_at.strftime('%Y-%m-%d')}"