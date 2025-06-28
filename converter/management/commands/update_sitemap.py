# converter/management/commands/update_sitemap.py
# Create this file to manually update sitemap and ping search engines

import os
from django.core.management.base import BaseCommand
from django.contrib.sitemaps import ping_google
from django.conf import settings
import requests
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Updates sitemap and pings search engines'

    def add_arguments(self, parser):
        parser.add_argument(
            '--ping-google',
            action='store_true',
            help='Ping Google about sitemap update',
        )
        parser.add_argument(
            '--ping-bing',
            action='store_true',
            help='Ping Bing about sitemap update',
        )

    def handle(self, *args, **options):
        site_domain = getattr(settings, 'SITE_DOMAIN', 'jpg2pdf.at')
        protocol = 'https' if getattr(settings, 'SITEMAP_USE_HTTPS', True) else 'http'
        sitemap_url = f"{protocol}://{site_domain}/sitemap.xml"
        
        self.stdout.write(f"Sitemap URL: {sitemap_url}")
        
        # Ping Google
        if options['ping_google']:
            try:
                ping_google()
                self.stdout.write(
                    self.style.SUCCESS('Successfully pinged Google about sitemap update')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to ping Google: {e}')
                )
        
        # Ping Bing
        if options['ping_bing']:
            try:
                bing_ping_url = f"http://www.bing.com/ping?sitemap={sitemap_url}"
                response = requests.get(bing_ping_url, timeout=10)
                if response.status_code == 200:
                    self.stdout.write(
                        self.style.SUCCESS('Successfully pinged Bing about sitemap update')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Bing ping returned status: {response.status_code}')
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to ping Bing: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Sitemap update process completed')
        )