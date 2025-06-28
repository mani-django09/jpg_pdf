# converter/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils import timezone
import json
import os
import uuid
import tempfile
import logging
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from io import BytesIO
from django.contrib import messages
from django.core.mail import send_mail


try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False
    
from .models import ConversionJob

# Set up logging
logger = logging.getLogger(__name__)

def home(request):
    """Main homepage with conversion options"""
    return render(request, 'converter/home.html')

@csrf_exempt
@require_http_methods(["POST"])
def upload_file(request):
    """Handle file upload and initiate conversion"""
    try:
        # Check if file is in request
        if 'file' not in request.FILES:
            return JsonResponse({'success': False, 'error': 'No file uploaded'}, status=400)
        
        uploaded_file = request.FILES['file']
        conversion_type = request.POST.get('conversion_type', 'jpg_to_pdf')
        
        # Validate file size
        if uploaded_file.size > 50 * 1024 * 1024:  # 50MB limit
            return JsonResponse({
                'success': False, 
                'error': 'File too large. Maximum size is 50MB.'
            }, status=400)
        
        # Validate file type
        if not validate_file_type(uploaded_file):
            return JsonResponse({
                'success': False, 
                'error': 'Unsupported file type. Please upload JPG, PNG, GIF, or PDF files.'
            }, status=400)
        
        # Create conversion job
        job = ConversionJob.objects.create(
            conversion_type=conversion_type,
            original_filename=uploaded_file.name,
            file_size=uploaded_file.size,
            status='pending'
        )
        
        logger.info(f"Created conversion job {job.id} for file {uploaded_file.name}")
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save uploaded file with unique name
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        unique_filename = f"{job.id}_{uuid.uuid4().hex[:8]}{file_extension}"
        file_path = os.path.join('uploads', unique_filename)
        
        try:
            saved_path = default_storage.save(file_path, uploaded_file)
            logger.info(f"Saved file to {saved_path}")
        except Exception as e:
            logger.error(f"Failed to save file: {str(e)}")
            job.delete()
            return JsonResponse({
                'success': False, 
                'error': 'Failed to save uploaded file'
            }, status=500)
        
        # Process conversion
        try:
            job.status = 'processing'
            job.save()
            
            result_path = process_conversion(saved_path, conversion_type, job.id)
            
            job.converted_filename = os.path.basename(result_path)
            job.status = 'completed'
            job.completed_at = timezone.now()
            job.save()
            
            logger.info(f"Conversion completed for job {job.id}")
            
            return JsonResponse({
                'success': True,
                'job_id': str(job.id),
                'download_url': f'/download/{job.id}/',
                'original_filename': job.original_filename,
                'converted_filename': job.converted_filename
            })
            
        except Exception as e:
            logger.error(f"Conversion failed for job {job.id}: {str(e)}")
            job.status = 'failed'
            job.error_message = str(e)
            job.save()
            
            # Clean up uploaded file
            try:
                if default_storage.exists(saved_path):
                    default_storage.delete(saved_path)
            except:
                pass
                
            return JsonResponse({
                'success': False, 
                'error': f'Conversion failed: {str(e)}'
            }, status=500)
            
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        return JsonResponse({
            'success': False, 
            'error': f'Upload failed: {str(e)}'
        }, status=500)

def validate_file_type(uploaded_file):
    """Validate file type based on extension and content"""
    # Get file extension
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.pdf']
    
    if file_extension not in allowed_extensions:
        return False
    
    # If python-magic is available, check MIME type
    if HAS_MAGIC:
        try:
            uploaded_file.seek(0)
            file_content = uploaded_file.read(1024)  # Read first 1KB
            uploaded_file.seek(0)  # Reset file pointer
            
            mime_type = magic.from_buffer(file_content, mime=True)
            allowed_mime_types = [
                'image/jpeg', 'image/png', 'image/gif', 
                'image/bmp', 'image/webp', 'application/pdf'
            ]
            
            return mime_type in allowed_mime_types
        except Exception as e:
            logger.warning(f"MIME type detection failed: {str(e)}")
            # Fall back to extension-based validation
            pass
    
    return True

def download_file(request, job_id):
    """Download converted file"""
    try:
        job = get_object_or_404(ConversionJob, id=job_id)
        
        if job.status != 'completed':
            raise Http404("File not ready or conversion failed")
        
        if not job.converted_filename:
            raise Http404("Converted file not found")
        
        file_path = os.path.join(settings.MEDIA_ROOT, 'converted', job.converted_filename)
        
        if not os.path.exists(file_path):
            logger.error(f"Converted file not found: {file_path}")
            raise Http404("File not found")
        
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
                
            response = HttpResponse(file_content)
            
            # Set appropriate content type
            if job.converted_filename.endswith('.pdf'):
                response['Content-Type'] = 'application/pdf'
            elif job.converted_filename.endswith(('.jpg', '.jpeg')):
                response['Content-Type'] = 'image/jpeg'
            elif job.converted_filename.endswith('.png'):
                response['Content-Type'] = 'image/png'
            else:
                response['Content-Type'] = 'application/octet-stream'
            
            response['Content-Disposition'] = f'attachment; filename="{job.converted_filename}"'
            response['Content-Length'] = len(file_content)
            
            logger.info(f"File {job.converted_filename} downloaded successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            raise Http404("Error reading file")
        
    except Http404:
        raise
    except Exception as e:
        logger.error(f"Download failed for job {job_id}: {str(e)}")
        raise Http404("Download failed")

def job_status(request, job_id):
    """Get job status via AJAX"""
    try:
        job = get_object_or_404(ConversionJob, id=job_id)
        return JsonResponse({
            'status': job.status,
            'original_filename': job.original_filename,
            'converted_filename': job.converted_filename,
            'error_message': job.error_message,
            'created_at': job.created_at.isoformat(),
            'completed_at': job.completed_at.isoformat() if job.completed_at else None
        })
    except Exception as e:
        logger.error(f"Status check failed for job {job_id}: {str(e)}")
        return JsonResponse({'error': 'Job not found'}, status=404)

def process_conversion(input_path, conversion_type, job_id):
    """Process file conversion based on type"""
    input_full_path = os.path.join(settings.MEDIA_ROOT, input_path)
    output_dir = os.path.join(settings.MEDIA_ROOT, 'converted')
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        if conversion_type in ['jpg_to_pdf', 'png_to_pdf']:
            return convert_image_to_pdf(input_full_path, output_dir, job_id)
        elif conversion_type == 'resize_image':
            return resize_image(input_full_path, output_dir, job_id)
        elif conversion_type == 'compress_image':
            return compress_image(input_full_path, output_dir, job_id)
        else:
            raise ValueError(f"Unsupported conversion type: {conversion_type}")
    except Exception as e:
        logger.error(f"Conversion processing failed: {str(e)}")
        raise

def convert_image_to_pdf(input_path, output_dir, job_id):
    """Convert image to PDF"""
    try:
        with Image.open(input_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparent images
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if 'transparency' in img.info:
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            output_filename = f"{job_id}_converted.pdf"
            output_path = os.path.join(output_dir, output_filename)
            
            # Get image dimensions
            img_width, img_height = img.size
            
            # Calculate appropriate page size (convert pixels to points, assuming 72 DPI)
            # Limit maximum size to A4 for reasonable file sizes
            max_width, max_height = A4  # A4 size in points
            
            # Calculate scaling factor to fit within A4
            scale_w = max_width / img_width
            scale_h = max_height / img_height
            scale = min(scale_w, scale_h, 1.0)  # Don't upscale
            
            pdf_width = img_width * scale
            pdf_height = img_height * scale
            
            # Create PDF
            c = canvas.Canvas(output_path, pagesize=(pdf_width, pdf_height))
            
            # Use temporary file for image processing
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                temp_img_path = temp_file.name
                
                try:
                    # Save image as JPEG for PDF embedding
                    img.save(temp_img_path, "JPEG", quality=95, optimize=True)
                    
                    # Add image to PDF
                    c.drawImage(temp_img_path, 0, 0, width=pdf_width, height=pdf_height)
                    c.save()
                    
                finally:
                    # Clean up temp file
                    try:
                        os.unlink(temp_img_path)
                    except:
                        pass
            
            logger.info(f"Successfully converted image to PDF: {output_path}")
            return output_path
            
    except Exception as e:
        logger.error(f"Image to PDF conversion failed: {str(e)}")
        raise Exception(f"Failed to convert image to PDF: {str(e)}")

def resize_image(input_path, output_dir, job_id, max_size=(1920, 1080)):
    """Resize image while maintaining aspect ratio"""
    try:
        with Image.open(input_path) as img:
            # Keep original format if possible
            original_format = img.format
            
            # Create a copy and resize
            img_copy = img.copy()
            img_copy.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Determine output format and filename
            if original_format in ['JPEG', 'JPG']:
                output_filename = f"{job_id}_resized.jpg"
                save_format = "JPEG"
                save_kwargs = {"quality": 90, "optimize": True}
            elif original_format == 'PNG':
                output_filename = f"{job_id}_resized.png"
                save_format = "PNG"
                save_kwargs = {"optimize": True}
            else:
                # Default to JPEG for other formats
                output_filename = f"{job_id}_resized.jpg"
                save_format = "JPEG"
                if img_copy.mode in ('RGBA', 'LA', 'P'):
                    img_copy = img_copy.convert('RGB')
                save_kwargs = {"quality": 90, "optimize": True}
            
            output_path = os.path.join(output_dir, output_filename)
            img_copy.save(output_path, save_format, **save_kwargs)
            
            logger.info(f"Successfully resized image: {output_path}")
            return output_path
            
    except Exception as e:
        logger.error(f"Image resize failed: {str(e)}")
        raise Exception(f"Failed to resize image: {str(e)}")

def compress_image(input_path, output_dir, job_id, quality=75):
    """Compress image to reduce file size"""
    try:
        with Image.open(input_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if 'transparency' in img.info:
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            output_filename = f"{job_id}_compressed.jpg"
            output_path = os.path.join(output_dir, output_filename)
            
            # Save with compression
            img.save(output_path, "JPEG", quality=quality, optimize=True)
            
            logger.info(f"Successfully compressed image: {output_path}")
            return output_path
            
    except Exception as e:
        logger.error(f"Image compression failed: {str(e)}")
        raise Exception(f"Failed to compress image: {str(e)}")

# Cleanup function to remove old files (can be called via management command)
def cleanup_old_files():
    """Remove files older than 24 hours"""
    try:
        from datetime import timedelta
        cutoff_time = timezone.now() - timedelta(hours=24)
        
        old_jobs = ConversionJob.objects.filter(created_at__lt=cutoff_time)
        
        for job in old_jobs:
            # Delete associated files
            try:
                if job.converted_filename:
                    converted_path = os.path.join(settings.MEDIA_ROOT, 'converted', job.converted_filename)
                    if os.path.exists(converted_path):
                        os.remove(converted_path)
                
                # Delete uploaded file
                upload_path = os.path.join(settings.MEDIA_ROOT, 'uploads', f"{job.id}_*")
                import glob
                for file_path in glob.glob(upload_path):
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        
            except Exception as e:
                logger.warning(f"Failed to delete files for job {job.id}: {str(e)}")
            
            # Delete job record
            job.delete()
        
        logger.info(f"Cleaned up {old_jobs.count()} old conversion jobs")
        
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")

# Error handler for development
def handle_conversion_error(request, exception):
    """Custom error handler for conversion errors"""
    logger.error(f"Conversion error: {str(exception)}")
    
    if request.headers.get('Content-Type') == 'application/json':
        return JsonResponse({
            'success': False,
            'error': 'An error occurred during file conversion. Please try again.'
        }, status=500)
    else:
        return render(request, 'converter/error.html', {
            'error_message': 'An error occurred during file conversion.'
        })

def privacy_policy(request):
    """Privacy Policy page"""
    return render(request, 'converter/privacy_policy.html', {
        'page_title': 'Privacy Policy - JPG to PDF Converter',
        'meta_description': 'Privacy Policy for jpg2pdf.at JPG to PDF converter. Learn how we protect your data during JPG to PDF conversion.',
    })

def terms_of_service(request):
    """Terms of Service page"""
    return render(request, 'converter/terms_of_service.html', {
        'page_title': 'Terms of Service - JPG to PDF Converter',
        'meta_description': 'Terms of Service for jpg2pdf.at JPG to PDF converter. Legal terms and conditions for using our service.',
    })

def contact_us(request):
    """Contact Us page"""
    return render(request, 'converter/contact_us.html', {
        'page_title': 'Contact Us - JPG to PDF Converter Support',
        'meta_description': 'Contact jpg2pdf.at for support with JPG to PDF conversion, feedback, or questions.',
    })

@csrf_exempt
@require_http_methods(["POST"])
def contact_submit(request):
    """Handle contact form submission"""
    try:
        # Get form data
        inquiry_type = request.POST.get('inquiry_type', '')
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        
        # Basic validation
        if not all([inquiry_type, name, email, subject, message]):
            return JsonResponse({
                'success': False,
                'error': 'All fields are required.'
            }, status=400)
        
        # Email validation
        import re
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, email):
            return JsonResponse({
                'success': False,
                'error': 'Please enter a valid email address.'
            }, status=400)
        
        # Message length validation
        if len(message) < 10:
            return JsonResponse({
                'success': False,
                'error': 'Message must be at least 10 characters long.'
            }, status=400)
        
        if len(message) > 2000:
            return JsonResponse({
                'success': False,
                'error': 'Message must be less than 2000 characters.'
            }, status=400)
        
        # Prepare email content
        inquiry_types = {
            'technical_support': 'Technical Support - JPG to PDF Issues',
            'feature_request': 'Feature Request',
            'bug_report': 'Bug Report',
            'privacy_question': 'Privacy Question',
            'business_inquiry': 'Business Inquiry',
            'feedback': 'General Feedback',
            'other': 'Other'
        }
        
        inquiry_type_display = inquiry_types.get(inquiry_type, 'Other')
        
        # Email to admin
        admin_subject = f'[jpg2pdf.at] {inquiry_type_display}: {subject}'
        admin_message = f"""
New contact form submission from jpg2pdf.at:

Type: {inquiry_type_display}
Name: {name}
Email: {email}
Subject: {subject}

Message:
{message}

---
Sent from jpg2pdf.at contact form
IP: {request.META.get('REMOTE_ADDR', 'Unknown')}
User Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}
"""
        
        # Auto-reply to user
        user_subject = f'Thank you for contacting jpg2pdf.at - {subject}'
        user_message = f"""
Dear {name},

Thank you for contacting jpg2pdf.at! We have received your message regarding: {subject}

Inquiry Type: {inquiry_type_display}

We will review your message and respond within 24 hours. For technical issues, we typically respond within 4 hours during business hours.

If you have any urgent concerns, please reply to this email.

Your message:
"{message}"

Best regards,
The jpg2pdf.at Team

---
This is an automated response. Please do not reply to this email.
For support, contact us at support@jpg2pdf.at
"""
        
        try:
            # Send email to admin (configure your email settings in Django settings)
            send_mail(
                admin_subject,
                admin_message,
                settings.DEFAULT_FROM_EMAIL,
                ['support@jpg2pdf.at'],  # Replace with your admin email
                fail_silently=False,
            )
            
            # Send auto-reply to user
            send_mail(
                user_subject,
                user_message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=True,  # Don't fail if user email fails
            )
            
            logger.info(f"Contact form submitted successfully: {inquiry_type} from {email}")
            
        except Exception as email_error:
            logger.error(f"Failed to send contact form email: {email_error}")
            # Still return success to user, but log the error
            
        return JsonResponse({
            'success': True,
            'message': 'Thank you for your message! We will respond within 24 hours.'
        })
        
    except Exception as e:
        logger.error(f"Contact form submission error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while sending your message. Please try again or contact us directly at support@jpg2pdf.at'
        }, status=500)
    
# Add this to your converter/views.py file

from django.http import HttpResponse
from django.template.loader import render_to_string

def robots_txt(request):
    """Serve robots.txt file"""
    content = """# robots.txt for jpg2pdf.at
# JPG to PDF Converter Website

User-agent: *
Allow: /

# Allow all major search engines
User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: Slurp
Allow: /

User-agent: DuckDuckBot
Allow: /

User-agent: Baiduspider
Allow: /

User-agent: YandexBot
Allow: /

User-agent: facebookexternalhit
Allow: /

# Disallow admin and sensitive areas
Disallow: /admin/
Disallow: /static/admin/
Disallow: /media/uploads/
Disallow: /media/converted/
Disallow: /download/
Disallow: /upload/
Disallow: /status/

# Disallow common technical files
Disallow: /*.json$
Disallow: /api/
Disallow: /ajax/

# Allow important pages and directories
Allow: /static/css/
Allow: /static/js/
Allow: /static/images/
Allow: /favicon.ico
Allow: /apple-touch-icon.png
Allow: /site.webmanifest

# Security - Block sensitive file types
Disallow: /*.sql$
Disallow: /*.log$
Disallow: /*.bak$
Disallow: /*.conf$
Disallow: /*.ini$

# Block common attack vectors
Disallow: /wp-admin/
Disallow: /wp-login.php
Disallow: /phpMyAdmin/
Disallow: /.env
Disallow: /.git/

# Sitemap location
Sitemap: {protocol}://{domain}/sitemap.xml

# Crawl delay for polite crawling
Crawl-delay: 1""".format(
        protocol='https' if request.is_secure() else 'http',
        domain=request.get_host()
    )
    
    return HttpResponse(content, content_type="text/plain")