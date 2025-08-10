from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import json
import requests
from .models import Project, BlogPost, ContactMessage, NewsletterSubscriber, NewsletterCampaign, ProjectRAG
from .forms import ContactForm, NewsletterSubscriptionForm
from .newsletter_utils import get_top_article, send_welcome_email, send_newsletter_to_all, send_test_email, send_blog_post_newsletter

# Check if RAG dependencies are available
def check_rag_availability():
    """Check if RAG dependencies are available with detailed error reporting"""
    required_packages = {
        'numpy': 'import numpy as np',
        'faiss': 'import faiss',
        'openai': 'from openai import OpenAI',
        'groq': 'from groq import Groq',
        'tiktoken': 'import tiktoken'
    }
    
    failed_packages = []
    
    for package_name, import_statement in required_packages.items():
        try:
            exec(import_statement)
            print(f"✅ {package_name}: OK")
        except Exception as e:
            print(f"❌ {package_name}: {e}")
            failed_packages.append(package_name)
    
    if failed_packages:
        print(f"❌ Failed packages: {', '.join(failed_packages)}")
        if 'openai' in failed_packages:
            print("💡 To fix openai: pip install openai")
        return False
    
    print("✅ All RAG dependencies loaded successfully!")
    return True

RAG_AVAILABLE = check_rag_availability()
print(f"RAG_AVAILABLE = {RAG_AVAILABLE}")


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


def project_chatbot(request, pk):
    """Project-specific RAG chatbot page"""
    project = get_object_or_404(Project, pk=pk)
    print(f"🤖 Project chatbot request for: {project.title} (ID: {pk})")

    # Check if project has GitHub URL
    print(f"🔗 GitHub URL: {project.github_url}")
    if not project.github_url:
        print("❌ No GitHub URL - redirecting")
        messages.error(request, 'This project does not have a GitHub repository for discussion.')
        return redirect('project_detail', pk=pk)

    # Check if RAG functionality is available
    print(f"🔍 RAG_AVAILABLE: {RAG_AVAILABLE}")
    if not RAG_AVAILABLE:
        print("❌ RAG dependencies not available - providing fallback chatbot")
        messages.warning(request, 'Advanced AI analysis is currently unavailable. Using basic project information for discussion.')
        
        # Use fallback chatbot without RAG
        return render(request, 'portfolio/project_chatbot.html', {
            'project': project,
            'fallback_mode': True
        })

    # Check if RAG data exists and is processed
    try:
        rag_data = project.rag_data
        print(f"📊 RAG data exists: True, is_processed: {rag_data.is_processed}")
        if not rag_data.is_processed:
            print("🔄 RAG data not processed - starting processing")
            messages.info(request, 'Preparing AI assistant for this project. Please wait while we analyze the repository...')
            
            # Process RAG data in the background
            try:
                from django.core.management import call_command
                call_command('process_project_rag', project_id=pk)
                
                # Re-check if processing completed
                rag_data.refresh_from_db()
                if rag_data.is_processed:
                    messages.success(request, 'AI assistant is ready! You can now ask questions about this project.')
                else:
                    messages.warning(request, 'Repository analysis is in progress. Please try again in a few minutes.')
                    return redirect('project_detail', pk=pk)
            except Exception as e:
                print(f"❌ Error processing RAG data: {e}")
                messages.error(request, 'Failed to analyze repository. Please try again later.')
                return redirect('project_detail', pk=pk)
                
    except ProjectRAG.DoesNotExist:
        print("❌ No RAG data exists - creating and processing")
        messages.info(request, 'Setting up AI assistant for this project. Analyzing repository...')
        
        try:
            # Create RAG data entry
            ProjectRAG.objects.create(
                project=project,
                repo_content='',
                embeddings_data='',
                is_processed=False
            )
            
            # Process RAG data
            from django.core.management import call_command
            call_command('process_project_rag', project_id=pk)
            
            # Check if processing completed
            try:
                rag_data = project.rag_data
                rag_data.refresh_from_db()
                if rag_data.is_processed:
                    messages.success(request, 'AI assistant is ready! You can now ask questions about this project.')
                else:
                    messages.warning(request, 'Repository analysis is in progress. Please try again in a few minutes.')
                    return redirect('project_detail', pk=pk)
            except:
                messages.error(request, 'Failed to analyze repository. Please try again later.')
                return redirect('project_detail', pk=pk)
                
        except Exception as e:
            print(f"❌ Error creating/processing RAG data: {e}")
            messages.error(request, 'Failed to set up AI assistant. Please try again later.')
            return redirect('project_detail', pk=pk)

    print("✅ All checks passed - rendering project chatbot page")
    return render(request, 'portfolio/project_chatbot.html', {
        'project': project
    })


@csrf_exempt
@require_http_methods(["POST"])
def project_chatbot_ask(request, pk):
    """Handle project-specific RAG chatbot queries"""
    try:
        project = get_object_or_404(Project, pk=pk)
        data = json.loads(request.body)
        user_message = data.get('message', '')
        chat_history = data.get('chat_history', [])

        if not user_message:
            return JsonResponse({
                'error': 'No message provided',
                'status': 'error'
            }, status=400)

        # Check if RAG functionality is available
        if not RAG_AVAILABLE:
            # Provide basic fallback response using project information
            basic_response = f"""I can help you with general questions about the **{project.title}** project.

**Project Description:**
{project.description}

**Technologies Used:** {', '.join([tag.name for tag in project.tags.all()])}

**Repository:** {project.github_url}

Since advanced code analysis is currently unavailable, I can provide general information about the project. For specific code questions, please visit the GitHub repository directly.

What would you like to know about this project?"""
            
            return JsonResponse({
                'response': basic_response,
                'status': 'success'
            })

        # Check if RAG data exists and is processed
        try:
            rag_data = project.rag_data
            if not rag_data.is_processed:
                return JsonResponse({
                    'response': 'The project repository is still being processed. Please try again later.',
                    'status': 'success'
                })
        except ProjectRAG.DoesNotExist:
            return JsonResponse({
                'response': 'The project repository data is not available. Please contact the administrator.',
                'status': 'success'
            })

        # Import RAG dependencies locally
        try:
            import numpy as np
            import faiss
            from .rag_service import ProjectRAGService
        except (ImportError, SyntaxError, Exception) as e:
            return JsonResponse({
                'response': f'The RAG system is currently unavailable due to dependency issues: {str(e)}',
                'status': 'success'
            })

        # Initialize RAG service
        rag_service = ProjectRAGService()

        # Get embeddings data
        embeddings_data = rag_data.get_embeddings_data()
        if not embeddings_data:
            return JsonResponse({
                'response': 'Sorry, there was an issue accessing the project data. Please try again later.',
                'status': 'success'
            })

        # Reconstruct FAISS index
        chunks = embeddings_data.get('chunks', [])
        embeddings_list = embeddings_data.get('embeddings', [])

        if not chunks or not embeddings_list:
            return JsonResponse({
                'response': 'Sorry, the project data is incomplete. Please contact the administrator.',
                'status': 'success'
            })

        # Convert embeddings back to numpy array
        embeddings = np.array(embeddings_list, dtype=np.float32)

        # Create FAISS index
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings)

        # Search for relevant chunks
        similar_chunks = rag_service.search_similar_chunks(
            user_message, index, chunks, top_k=5
        )

        if not similar_chunks:
            return JsonResponse({
                'response': f'I couldn\'t find relevant information about "{user_message}" in the {project.title} repository. Could you try rephrasing your question or ask about specific files, functions, or features?',
                'status': 'success'
            })

        # Extract just the chunk text for context
        context_chunks = [chunk for chunk, _ in similar_chunks]

        # Generate response using Groq with chat history
        response = rag_service.generate_response_with_groq(
            user_message, context_chunks, project.title, chat_history
        )

        return JsonResponse({
            'response': response,
            'status': 'success'
        })

    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)


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


def newsletter(request):
    """Newsletter subscription page"""
    if request.method == 'POST':
        form = NewsletterSubscriptionForm(request.POST)
        if form.is_valid():
            try:
                # Check if email already exists
                email = form.cleaned_data['email']
                if NewsletterSubscriber.objects.filter(email=email).exists():
                    messages.error(request, 'This email address is already subscribed.')
                    return redirect('newsletter')

                # Save new subscriber
                subscriber = form.save()

                # Send welcome email
                welcome_sent = send_welcome_email(subscriber)

                if welcome_sent:
                    messages.success(request, '🎉 You have successfully subscribed! Check your email for a welcome message.')
                else:
                    messages.success(request, '🎉 You have successfully subscribed! Welcome email will be sent shortly.')

                return redirect('newsletter')

            except Exception as e:
                print(f"Error during subscription: {e}")
                messages.error(request, 'An error occurred. Please try again.')
    else:
        form = NewsletterSubscriptionForm()

    # Get today's featured article for preview
    try:
        article_title, article_link = get_top_article()
    except:
        article_title, article_link = "Preview not available", "#"

    return render(request, 'portfolio/newsletter.html', {
        'form': form,
        'article_title': article_title,
        'article_link': article_link
    })


def is_admin_user(user):
    """Check if user is staff or superuser"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def newsletter_admin_login_required(view_func):
    """Custom decorator for newsletter admin views"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to access the newsletter admin dashboard.')
            return redirect('/admin/login/?next=' + request.path)
        elif not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, 'You do not have permission to access the newsletter admin dashboard.')
            return redirect('newsletter')
        return view_func(request, *args, **kwargs)
    return wrapper


@newsletter_admin_login_required
def newsletter_admin(request):
    """Newsletter admin dashboard"""
    subscribers = NewsletterSubscriber.objects.filter(is_active=True)
    recent_campaigns = NewsletterCampaign.objects.all()[:5]

    # Get recent blog posts
    recent_blog_posts = BlogPost.objects.all()[:10]

    # Get today's article for preview
    try:
        article_title, article_link = get_top_article()
    except:
        article_title, article_link = "Unable to fetch article", "#"

    context = {
        'subscribers': subscribers,
        'subscriber_count': subscribers.count(),
        'recent_campaigns': recent_campaigns,
        'recent_blog_posts': recent_blog_posts,
        'article_title': article_title,
        'article_link': article_link
    }

    return render(request, 'portfolio/newsletter_admin.html', context)


@newsletter_admin_login_required
@require_http_methods(["POST"])
def send_newsletter(request):
    """Send newsletter to all subscribers"""
    try:
        print("🚀 Newsletter send request received")
        
        # Check email configuration first
        from django.conf import settings
        print(f"📧 Email config check - USER: {bool(settings.EMAIL_HOST_USER)}, PASSWORD: {bool(settings.EMAIL_HOST_PASSWORD)}")
        
        if not settings.EMAIL_HOST_USER:
            print("❌ EMAIL_HOST_USER not configured")
            messages.error(request, '❌ EMAIL_HOST_USER not configured. Please add your Gmail address to .env file.')
            return redirect('newsletter_admin')

        if not settings.EMAIL_HOST_PASSWORD:
            print("❌ EMAIL_HOST_PASSWORD not configured")
            messages.error(request, '❌ EMAIL_HOST_PASSWORD not configured. Please add your Gmail app password to .env file.')
            return redirect('newsletter_admin')

        print("📬 Calling send_newsletter_to_all...")
        success_count, total_count, campaign = send_newsletter_to_all()
        print(f"📊 Results received: {success_count}/{total_count}")

        if success_count > 0:
            print(f"✅ Newsletter sent successfully to {success_count} subscribers")
            messages.success(request, f'✅ Successfully sent {success_count} out of {total_count} emails!')
        elif total_count == 0:
            print("⚠️ No active subscribers found")
            messages.warning(request, '⚠️ No active subscribers found.')
        else:
            print("❌ All emails failed to send")
            messages.error(request, '❌ Failed to send emails. Check the console for detailed error messages.')

    except Exception as e:
        print(f"❌ Exception in send_newsletter view: {e}")
        print(f"❌ Exception type: {type(e).__name__}")
        messages.error(request, f'Error sending newsletter: {str(e)}')

    return redirect('newsletter_admin')


@newsletter_admin_login_required
@require_http_methods(["POST"])
def send_blog_post_to_newsletter(request, blog_id):
    """Send a specific blog post to newsletter subscribers"""
    try:
        blog_post = get_object_or_404(BlogPost, id=blog_id)

        # Check email configuration first
        from django.conf import settings
        if not settings.EMAIL_HOST_USER:
            messages.error(request, '❌ EMAIL_HOST_USER not configured. Please add your Gmail address to .env file.')
            return redirect('newsletter_admin')

        if not settings.EMAIL_HOST_PASSWORD:
            messages.error(request, '❌ EMAIL_HOST_PASSWORD not configured. Please add your Gmail app password to .env file.')
            return redirect('newsletter_admin')

        # Check if already sent
        if blog_post.sent_to_newsletter:
            messages.warning(request, f'📧 Blog post "{blog_post.title}" has already been sent to newsletter subscribers.')
            return redirect('newsletter_admin')

        # Send to newsletter subscribers
        success_count, total_count, campaign = send_blog_post_newsletter(blog_post)

        if success_count > 0:
            messages.success(request, f'✅ Successfully sent "{blog_post.title}" to {success_count} out of {total_count} subscribers!')
        elif total_count == 0:
            messages.warning(request, '⚠️ No active subscribers found.')
        else:
            messages.error(request, '❌ Failed to send blog post newsletter. Check the console for detailed error messages.')

    except Exception as e:
        messages.error(request, f'Error sending blog post newsletter: {str(e)}')

    return redirect('newsletter_admin')


@newsletter_admin_login_required
@require_http_methods(["POST"])
def send_test_newsletter(request):
    """Send test newsletter"""
    test_email = request.POST.get('test_email')

    if not test_email or '@' not in test_email:
        messages.error(request, 'Please enter a valid email address for testing.')
    else:
        if send_test_email(test_email):
            messages.success(request, '✅ Test email sent successfully!')
        else:
            messages.error(request, '❌ Failed to send test email.')

    return redirect('newsletter_admin')