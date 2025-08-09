from django.contrib import admin
from django.utils.html import format_html
from .models import Project, ProjectImage, BlogPost, ContactMessage, NewsletterSubscriber, NewsletterCampaign


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
    list_display = ('title', 'slug', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'content')
    readonly_fields = ('created_at', 'updated_at', 'slug')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'content', 'cover_image')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


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