from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import json
import requests
from .models import Project, BlogPost, ContactMessage
from .forms import ContactForm


def send_contact_notification_sms(contact_message):
    """Send SMS notification when someone submits a contact form"""
    try:
        phone_number = settings.ADMIN_PHONE_NUMBER
        sender_name = contact_message.name
        sender_email = contact_message.email

        message = f"New contact message from {sender_name} ({sender_email}). Check your admin panel for details."

        # URL encode the message
        encoded_message = requests.utils.quote(message)

        key = settings.MNOTIFY_API_KEY
        sender_id = 'Afimpp-Tvet'  # Using your registered sender ID

        # Try with your registered sender ID first, then fallback if it fails
        url = f"https://apps.mnotify.net/smsapi?key={key}&to={phone_number}&msg={encoded_message}&sender_id={sender_id}"

        print(f"Sending SMS to: {phone_number}")
        print(f"Message: {message}")
        print(f"URL: {url}")

        response = requests.get(url)
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.text}")

        if response.status_code == 200:
            # Parse JSON response
            try:
                response_data = response.json()
                if response_data.get('status') == 'success':
                    print("SMS notification sent successfully")
                    return True
                elif response_data.get('message') == 'Invalid sender Id':
                    # Try with a fallback sender ID
                    print("Afimpp-Tvet sender ID failed, trying with fallback...")
                    fallback_url = f"https://apps.mnotify.net/smsapi?key={key}&to={phone_number}&msg={encoded_message}&sender_id=mNotify"
                    fallback_response = requests.get(fallback_url)
                    print(f"Fallback response: {fallback_response.text}")

                    if fallback_response.status_code == 200:
                        fallback_data = fallback_response.json()
                        if fallback_data.get('status') == 'success':
                            print("SMS sent successfully with fallback sender ID")
                            return True

                    print(f"Both sender IDs failed. You may need to check your sender ID registration with mnotify.")
                    return False
                else:
                    print(f"SMS API returned error: {response_data.get('message', 'Unknown error')}")
                    return False
            except:
                # If response is not JSON, check text content
                response_text = response.text.lower()
                if 'success' in response_text or 'sent' in response_text:
                    print("SMS notification sent successfully")
                    return True
                else:
                    print(f"SMS API returned 200 but with error message: {response.text}")
                    return False
        else:
            print(f"Failed to send SMS notification: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error sending SMS notification: {str(e)}")
        return False


def home(request):
    featured_projects = Project.objects.all()[:3]
    featured_blogs = BlogPost.objects.all()[:3]
    return render(request, 'portfolio/home.html', {
        'featured_projects': featured_projects,
        'featured_blogs': featured_blogs
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
            contact_message = form.save()

            # Send SMS notification
            send_contact_notification_sms(contact_message)

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