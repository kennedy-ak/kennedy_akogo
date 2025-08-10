from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('projects/', views.projects, name='projects'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/discuss/', views.project_chatbot, name='project_chatbot'),
    path('projects/<int:pk>/discuss/ask/', views.project_chatbot_ask, name='project_chatbot_ask'),
    path('services/', views.services, name='services'),
    path('blog/', views.blog, name='blog'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('contact/', views.contact, name='contact'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('chatbot/ask/', views.chatbot_ask, name='chatbot_ask'),
    path('newsletter/', views.newsletter, name='newsletter'),
    path('newsletter/admin/', views.newsletter_admin, name='newsletter_admin'),
    path('newsletter/send/', views.send_newsletter, name='send_newsletter'),
    path('newsletter/send-blog/<int:blog_id>/', views.send_blog_post_to_newsletter, name='send_blog_post_to_newsletter'),
    path('newsletter/test/', views.send_test_newsletter, name='send_test_newsletter'),
]