from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from .models import Project, ProjectImage, ProjectRAG, BlogPost, ContactMessage, NewsletterSubscriber, NewsletterCampaign

# Import RAG availability check
def check_rag_availability():
    try:
        import numpy as np
        import faiss
        from openai import OpenAI
        from groq import Groq
        return True
    except Exception as e:
        print(f"RAG dependencies not available in admin: {e}")
        return False

RAG_AVAILABLE = check_rag_availability()


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
        return "No image"
    image_preview.short_description = "Preview"


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at', 'rag_status')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ProjectImageInline]
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'tags')
        }),
        ('Links', {
            'fields': ('github_url', 'live_demo_url'),
            'description': 'Optional links to GitHub repository and live demo. Adding a GitHub URL will automatically set up AI discussion.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def rag_status(self, obj):
        """Show RAG processing status"""
        if not obj.github_url:
            return format_html('<span style="color: gray;">No GitHub URL</span>')
        
        try:
            rag_data = obj.rag_data
            if rag_data.is_processed:
                return format_html('<span style="color: green;">✅ AI Ready</span>')
            elif rag_data.processing_error:
                return format_html('<span style="color: red;">❌ Error</span>')
            else:
                return format_html('<span style="color: orange;">🔄 Processing</span>')
        except:
            return format_html('<span style="color: gray;">🕐 Pending</span>')
    rag_status.short_description = "AI Status"
    
    def save_model(self, request, obj, form, change):
        """Custom save method to handle RAG processing"""
        # Check if GitHub URL was added or changed
        github_url_changed = False
        if change:  # This is an update
            try:
                original_obj = Project.objects.get(pk=obj.pk)
                github_url_changed = original_obj.github_url != obj.github_url
            except Project.DoesNotExist:
                github_url_changed = False
        else:  # This is a new project
            github_url_changed = bool(obj.github_url)
        
        # Save the object first
        super().save_model(request, obj, form, change)
        
        # If GitHub URL was added or changed, set up RAG processing
        if github_url_changed and obj.github_url:
            print(f"🔄 GitHub URL added/changed for {obj.title} - setting up RAG processing")
            
            try:
                # Create or update RAG data entry
                from .models import ProjectRAG
                rag_data, created = ProjectRAG.objects.get_or_create(
                    project=obj,
                    defaults={
                        'repo_content': '',
                        'embeddings_data': '',
                        'is_processed': False,
                        'processing_error': 'Queued for processing',
                        'processing_status': 'pending'
                    }
                )
                
                if not created:
                    # Reset existing RAG data for reprocessing
                    rag_data.is_processed = False
                    rag_data.processing_error = 'Queued for reprocessing'
                    rag_data.save()
                
                messages.info(request, f'🤖 AI assistant setup queued for "{obj.title}". Repository analysis will begin shortly.')
                print(f"✅ RAG processing queued for project: {obj.title}")
                
                # Queue async processing
                try:
                    from .tasks import process_project_rag_async
                    process_project_rag_async.delay(obj.id)
                    messages.success(request, f'🚀 AI assistant queued for "{obj.title}". Processing will complete in the background.')
                except Exception as e:
                    print(f"❌ Failed to queue RAG processing: {e}")
                    messages.warning(request, 'AI assistant setup encountered an issue but will retry automatically.')
                        
            except Exception as e:
                print(f"❌ Error setting up RAG processing: {e}")
                messages.warning(request, 'AI assistant setup encountered an issue but will retry automatically.')


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'created_at', 'sent_to_newsletter', 'newsletter_status')
    list_filter = ('created_at', 'updated_at', 'sent_to_newsletter')
    search_fields = ('title', 'content')
    readonly_fields = ('created_at', 'updated_at', 'slug')

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'content', 'cover_image')
        }),
        ('Newsletter', {
            'fields': ('sent_to_newsletter',),
            'description': 'Check this box to automatically send this blog post to newsletter subscribers'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def newsletter_status(self, obj):
        if obj.sent_to_newsletter:
            return format_html('<span style="color: green;">✅ Sent</span>')
        else:
            return format_html('<span style="color: orange;">📧 Not Sent</span>')
    newsletter_status.short_description = "Newsletter Status"
    
    def save_model(self, request, obj, form, change):
        """Custom save method to handle newsletter sending"""
        # Check if this is an update and sent_to_newsletter was just checked
        was_sent_before = False
        if change:  # This is an update, not a new creation
            try:
                original_obj = BlogPost.objects.get(pk=obj.pk)
                was_sent_before = original_obj.sent_to_newsletter
            except BlogPost.DoesNotExist:
                was_sent_before = False
        
        # Save the object first
        super().save_model(request, obj, form, change)
        
        # If sent_to_newsletter was just checked (changed from False to True)
        if obj.sent_to_newsletter and not was_sent_before:
            print(f"📧 Sending blog post '{obj.title}' to newsletter subscribers...")
            
            # Import the newsletter sending function
            from .newsletter_utils import send_blog_post_newsletter
            from django.contrib import messages
            
            try:
                success_count, total_count, campaign = send_blog_post_newsletter(obj)
                
                if success_count > 0:
                    message = f'✅ Blog post "{obj.title}" sent to {success_count} out of {total_count} subscribers!'
                    messages.success(request, message)
                    print(f"✅ {message}")
                elif total_count == 0:
                    message = '⚠️ No active subscribers found.'
                    messages.warning(request, message)
                    print(f"⚠️ {message}")
                else:
                    message = '❌ Failed to send blog post newsletter. Check console for details.'
                    messages.error(request, message)
                    print(f"❌ {message}")
                    
            except Exception as e:
                error_message = f'❌ Error sending blog post newsletter: {str(e)}'
                messages.error(request, error_message)
                print(f"❌ {error_message}")
                
                # If sending failed, revert the sent_to_newsletter flag
                obj.sent_to_newsletter = False
                obj.save()


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at',)

    def has_add_permission(self, request):
        return False


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'is_active', 'subscribed_at')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('name', 'email', 'phone')
    readonly_fields = ('subscribed_at',)
    list_editable = ('is_active',)

    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'phone', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('subscribed_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(NewsletterCampaign)
class NewsletterCampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'sent_at', 'total_sent', 'success_count', 'success_rate')
    list_filter = ('sent_at', 'created_at')
    search_fields = ('title', 'subject', 'article_title')
    readonly_fields = ('created_at', 'success_rate')

    def success_rate(self, obj):
        if obj.total_sent > 0:
            rate = (obj.success_count / obj.total_sent) * 100
            return f"{rate:.1f}%"
        return "0%"
    success_rate.short_description = "Success Rate"

    fieldsets = (
        (None, {
            'fields': ('title', 'subject', 'content')
        }),
        ('Article Info', {
            'fields': ('article_title', 'article_link')
        }),
        ('Campaign Stats', {
            'fields': ('total_sent', 'success_count', 'success_rate', 'sent_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(ProjectRAG)
class ProjectRAGAdmin(admin.ModelAdmin):
    list_display = ('project', 'is_processed', 'last_updated', 'has_content', 'has_embeddings')
    list_filter = ('is_processed', 'last_updated')
    search_fields = ('project__title',)
    readonly_fields = ('last_updated', 'repo_content_preview', 'embeddings_info')

    fieldsets = (
        (None, {
            'fields': ('project', 'is_processed')
        }),
        ('Processing Status', {
            'fields': ('processing_error', 'last_updated'),
        }),
        ('Content Preview', {
            'fields': ('repo_content_preview',),
            'classes': ('collapse',)
        }),
        ('Embeddings Info', {
            'fields': ('embeddings_info',),
            'classes': ('collapse',)
        }),
    )

    def has_content(self, obj):
        return bool(obj.repo_content)
    has_content.boolean = True
    has_content.short_description = 'Has Content'

    def has_embeddings(self, obj):
        return bool(obj.embeddings_data)
    has_embeddings.boolean = True
    has_embeddings.short_description = 'Has Embeddings'

    def repo_content_preview(self, obj):
        if obj.repo_content:
            preview = obj.repo_content[:500] + "..." if len(obj.repo_content) > 500 else obj.repo_content
            return format_html('<pre style="white-space: pre-wrap; max-height: 200px; overflow-y: auto;">{}</pre>', preview)
        return "No content"
    repo_content_preview.short_description = "Repository Content Preview"

    def embeddings_info(self, obj):
        data = obj.get_embeddings_data()
        if data:
            return format_html(
                '<strong>Chunks:</strong> {}<br><strong>Embedding Dimension:</strong> {}',
                data.get('num_chunks', 0),
                data.get('embedding_dimension', 0)
            )
        return "No embeddings data"
    embeddings_info.short_description = "Embeddings Information"