"""
URL configuration for mysite project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from help_section.sitemap import StaticViewSitemap, FacilitySitemap

sitemaps = {
    'static': StaticViewSitemap,
    'facilities': FacilitySitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls), 
    path('help/', include('help_section.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
