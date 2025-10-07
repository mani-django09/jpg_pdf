# your_project/urls.py - Main project URLs file
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from converter.sitemaps import sitemaps
from django.conf.urls.i18n import i18n_patterns

# Non-translated URLs (sitemap, language switcher)
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, 
         name='django.contrib.sitemaps.views.sitemap'),
]

# Translated URLs with language prefix
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('converter.urls')),
    prefix_default_language=False  # Change to False to avoid /en/ prefix for English
)

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)