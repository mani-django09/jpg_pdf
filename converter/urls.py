# converter/urls.py - Updated with robots.txt only
from django.urls import path
from . import views

app_name = 'converter'

urlpatterns = [
    # Main application URLs
    path('', views.home, name='home'),
    path('upload/', views.upload_file, name='upload_file'),
    path('download/<uuid:job_id>/', views.download_file, name='download_file'),
    path('status/<uuid:job_id>/', views.job_status, name='job_status'),

    # Static pages
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('contact-us/', views.contact_us, name='contact_us'),
    path('contact/submit/', views.contact_submit, name='contact_submit'),
    
    # SEO files
    path('robots.txt', views.robots_txt, name='robots_txt'),
    

]