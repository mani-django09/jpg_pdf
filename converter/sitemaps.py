# converter/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 0.8
    changefreq = 'weekly'
    protocol = 'https'

    def items(self):
        return [
            'converter:home',
            'converter:privacy_policy', 
            'converter:terms_of_service',
            'converter:contact_us'
        ]

    def location(self, item):
        return reverse(item)

    def lastmod(self, item):
        # Return last modified date - you can customize this
        if item == 'converter:home':
            return timezone.now().date()
        return timezone.now().date() - timedelta(days=7)

    def priority(self, item):
        # Set priority based on page importance
        priorities = {
            'converter:home': 1.0,
            'converter:privacy_policy': 0.4,
            'converter:terms_of_service': 0.4,
            'converter:contact_us': 0.6
        }
        return priorities.get(item, 0.5)

    def changefreq(self, item):
        # Set change frequency based on page type
        frequencies = {
            'converter:home': 'daily',
            'converter:privacy_policy': 'monthly',
            'converter:terms_of_service': 'monthly', 
            'converter:contact_us': 'monthly'
        }
        return frequencies.get(item, 'weekly')


class ToolsSitemap(Sitemap):
    """Sitemap for conversion tools/services"""
    priority = 0.9
    changefreq = 'weekly'
    protocol = 'https'

    def items(self):
        return [
            'jpg-to-pdf',
            'png-to-pdf',
            'gif-to-pdf',
            'image-to-pdf',
            'batch-convert-jpg-to-pdf'
        ]

    def location(self, item):
        # All tools currently go to home page with fragments
        return reverse('converter:home')

    def lastmod(self, item):
        return timezone.now().date()

    def priority(self, item):
        # JPG to PDF is main service
        if item == 'jpg-to-pdf':
            return 1.0
        return 0.8


# Register sitemaps
sitemaps = {
    'static': StaticViewSitemap,
    'tools': ToolsSitemap,
}