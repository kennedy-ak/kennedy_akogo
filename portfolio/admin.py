from django.contrib import admin
from django.utils.html import format_html
from .models import Project, ProjectImage, ProjectRAG, BlogPost, ContactMessage, NewsletterSubscriber, NewsletterCampaign


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
    list_display = ('title', 'created_at', 'updated_at')
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
            'description': 'Optional links to GitHub repository and live demo'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


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
            'description': 'Newsletter sending status'
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