from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Facility


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return ['help_page', 'facility_categories', 'facility_map', 'search_facilities']

    def location(self, item):
        return reverse(item)


class FacilitySitemap(Sitemap):
    """Sitemap for facility detail pages"""
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return Facility.objects.all()

    def lastmod(self, obj):
        return obj.last_updated

    def location(self, obj):
        return reverse('facility_detail', args=[obj.slug])