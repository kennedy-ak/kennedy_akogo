from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Project, BlogPost, ContactMessage
from .forms import ContactForm


def home(request):
    featured_projects = Project.objects.all()[:3]
    return render(request, 'portfolio/home.html', {
        'featured_projects': featured_projects
    })


def projects(request):
    projects = Project.objects.all()
    return render(request, 'portfolio/projects.html', {
        'projects': projects
    })


def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'portfolio/project_detail.html', {
        'project': project
    })


def services(request):
    return render(request, 'portfolio/services.html')


def blog(request):
    blog_posts = BlogPost.objects.all()
    return render(request, 'portfolio/blog.html', {
        'blog_posts': blog_posts
    })


def blog_detail(request, slug):
    blog_post = get_object_or_404(BlogPost, slug=slug)
    return render(request, 'portfolio/blog_detail.html', {
        'blog_post': blog_post
    })


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')
    else:
        form = ContactForm()
    
    return render(request, 'portfolio/contact.html', {
        'form': form
    })


def chatbot(request):
    return render(request, 'portfolio/chatbot.html')


@csrf_exempt
@require_http_methods(["POST"])
def chatbot_ask(request):
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        # Mock response - replace with actual chatbot logic
        response = f"Thanks for your message: '{user_message}'. This is a placeholder response. You can integrate with OpenAI API or other AI services here."
        
        return JsonResponse({
            'response': response,
            'status': 'success'
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=400)