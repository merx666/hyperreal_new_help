from django import template
from django.db.models import Avg

register = template.Library()

@register.filter
def avg_rating(facility):
    """Calculate average rating for a facility."""
    if facility.ratings.exists():
        avg = facility.ratings.aggregate(Avg('value'))['value__avg']
        return round(avg, 1) if avg else 0
    return 0

@register.filter
def rating_stars(rating_value):
    """Convert rating value to star display."""
    try:
        rating = float(rating_value)
        full_stars = int(rating)
        half_star = 1 if rating - full_stars >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        
        stars = '⭐' * full_stars
        if half_star:
            stars += '⭐'
        
        return stars
    except (ValueError, TypeError):
        return ''

@register.filter
def rating_count(facility):
    """Get total number of ratings for a facility."""
    return facility.ratings.count()

@register.simple_tag
def rating_display(facility):
    """Display rating with stars and count."""
    avg = avg_rating(facility)
    count = rating_count(facility)
    
    if count == 0:
        return '<span class="text-muted">Brak ocen</span>'
    
    stars = rating_stars(avg)
    return f'<span class="facility-rating">{stars} <span class="rating-value">({avg})</span> <small class="text-muted">({count} ocen)</small></span>'