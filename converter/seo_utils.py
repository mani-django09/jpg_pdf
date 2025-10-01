# converter/seo_utils.py - Additional SEO utilities

from django.utils.html import format_html
from django.urls import reverse
from django.conf import settings

def generate_breadcrumbs(request, page_title=None):
    """Generate breadcrumb navigation for SEO"""
    breadcrumbs = [
        {'title': 'Home', 'url': reverse('converter:home'), 'active': False}
    ]
    
    path = request.path
    if path == '/privacy-policy/':
        breadcrumbs.append({'title': 'Privacy Policy', 'url': '', 'active': True})
    elif path == '/terms-of-service/':
        breadcrumbs.append({'title': 'Terms of Service', 'url': '', 'active': True})
    elif path == '/contact-us/':
        breadcrumbs.append({'title': 'Contact Us', 'url': '', 'active': True})
    elif page_title:
        breadcrumbs.append({'title': page_title, 'url': '', 'active': True})
    
    return breadcrumbs

def generate_structured_data(page_type='website', **kwargs):
    """Generate structured data for different page types"""
    
    base_data = {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": "JPG to PDF Converter",
        "alternateName": "jpg2pdf.link",
        "description": "Convert JPG images to PDF online for free. Fast, secure, and easy-to-use image to PDF converter.",
        "url": "https://jpg2pdf.link",
        "applicationCategory": "UtilityApplication",
        "operatingSystem": "Any",
        "browserRequirements": "Requires JavaScript. Modern browser recommended.",
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD",
            "availability": "https://schema.org/InStock"
        },
        "featureList": [
            "JPG to PDF conversion",
            "PNG to PDF conversion",
            "Batch conversion",
            "Free online tool",
            "No registration required",
            "Secure file processing"
        ],
        "publisher": {
            "@type": "Organization",
            "name": "JPG2PDF Converter",
            "url": "https://jpg2pdf.link"
        }
    }
    
    if page_type == 'faq':
        # Add FAQ structured data
        faq_data = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": "How do I convert JPG to PDF using jpg2pdf.link?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "Converting JPG to PDF at jpg2pdf.link is simple: upload your JPG images, click 'Convert JPG to PDF', and download your PDF file. Our online JPG to PDF converter handles the entire process automatically."
                    }
                },
                {
                    "@type": "Question", 
                    "name": "Is JPG to PDF conversion secure at jpg2pdf.link?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "Absolutely! Your JPG files are processed securely using encrypted connections. All uploaded JPG images and generated PDF files are automatically deleted from our servers within 24 hours."
                    }
                },
                {
                    "@type": "Question",
                    "name": "Do I need to register to use the JPG to PDF converter?",
                    "acceptedAnswer": {
                        "@type": "Answer", 
                        "text": "No registration required! Our JPG to PDF converter at jpg2pdf.link is completely free and anonymous. Simply upload your JPG images, convert to PDF, and download your file immediately."
                    }
                }
            ]
        }
        return faq_data
    
    elif page_type == 'howto':
        # Add HowTo structured data
        howto_data = {
            "@context": "https://schema.org",
            "@type": "HowTo",
            "name": "How to Convert JPG to PDF Online Free",
            "description": "Step-by-step guide to convert JPG images to PDF using jpg2pdf.link free online converter",
            "image": "https://jpg2pdf.link/static/images/jpg-to-pdf-guide.jpg",
            "totalTime": "PT2M",
            "estimatedCost": {
                "@type": "MonetaryAmount",
                "currency": "USD",
                "value": "0"
            },
            "step": [
                {
                    "@type": "HowToStep",
                    "name": "Upload JPG Images",
                    "text": "Click 'Select JPG Files' or drag and drop your images into the upload area",
                    "image": "https://jpg2pdf.link/static/images/step1-upload.jpg"
                },
                {
                    "@type": "HowToStep", 
                    "name": "Convert to PDF",
                    "text": "Click the 'Convert JPG to PDF' button to start the conversion process",
                    "image": "https://jpg2pdf.link/static/images/step2-convert.jpg"
                },
                {
                    "@type": "HowToStep",
                    "name": "Download PDF",
                    "text": "Download your converted PDF file instantly when the conversion is complete",
                    "image": "https://jpg2pdf.link/static/images/step3-download.jpg"
                }
            ]
        }
        return howto_data
    
    return base_data

def get_canonical_url(request, path_override=None):
    """Generate canonical URL for pages"""
    protocol = 'https' if request.is_secure() else 'http'
    domain = request.get_host()
    path = path_override or request.path
    
    return f"{protocol}://{domain}{path}"

def generate_meta_tags(request, title=None, description=None, keywords=None, **kwargs):
    """Generate meta tags for SEO"""
    default_title = "JPG to PDF Converter - Convert Images to PDF Online Free"
    default_description = "Convert JPG, PNG, GIF images to PDF online for free. Fast, secure, and easy-to-use image to PDF converter. No registration required."
    default_keywords = "jpg to pdf, png to pdf, image to pdf, convert images, pdf converter, online converter, free converter"
    
    meta_title = title or default_title
    meta_description = description or default_description 
    meta_keywords = keywords or default_keywords
    canonical_url = get_canonical_url(request)
    
    return {
        'title': meta_title,
        'description': meta_description,
        'keywords': meta_keywords,
        'canonical_url': canonical_url,
        'og_title': kwargs.get('og_title', meta_title),
        'og_description': kwargs.get('og_description', meta_description),
        'og_url': canonical_url,
        'twitter_title': kwargs.get('twitter_title', meta_title),
        'twitter_description': kwargs.get('twitter_description', meta_description),
    }