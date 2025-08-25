from django.templatetags.static import static
from django.urls import reverse
from jinja2 import Environment
from django.utils import timezone
from django.db.models import Avg

# Import custom filters
from help_section.templatetags.get_item import get_item
from help_section.templatetags.rating_filters import avg_rating, rating_stars

def environment(**options):
    env = Environment(**options)
    
    # Add global functions
    env.globals.update({
        'static': static,
        'url': reverse,
        'now': timezone.now,
    })
    
    # Add custom filters
    env.filters.update({
        'get_item': get_item,
        'avg_rating': avg_rating,
        'rating_stars': rating_stars,
        'rating_count': lambda facility: facility.ratings.count() if hasattr(facility, 'ratings') else 0,
    })
    
    return env