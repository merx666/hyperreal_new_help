from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Avg
from .models import Facility, Comment, RatingCategory, FacilityRating
from .forms import CommentForm, RatingForm

def help_view(request):
    now = timezone.now()
    context = {'now': now}
    return render(request, 'help_section/help_page.html', context)

def facility_categories_view(request):
    now = timezone.now()
    context = {'now': now}
    return render(request, 'help_section/facility_categories.html', context)

def facility_list_by_category(request, category_type, category_slug):
    # ... (kod tego widoku bez zmian) ...
    field_map = {
        'rodzaj-uzaleznien': 'addiction_types_text',
        'typ-placowki': 'facility_type_text',
        'wojewodztwo': 'voivodeship',
        'grupa-wiekowa-plec': 'other_activities_text',
        'rodzaj-leczenia': 'other_activities_text',
        'dlugosc-programu': 'program_lengths_text',
        'rodzaj-terapii': 'therapy_types_text',
        'poradnictwo': 'counseling_types_text',
        'psychoterapia': 'psychotherapy_types_text',
        'dzialania-prawne': 'other_activities_text',
        'inne-dzialania': 'other_activities_text',
    }
    db_field = field_map.get(category_type)
    if not db_field: raise Http404("Nieznany typ kategorii.")
    search_term = category_slug.replace('-', ' ')
    if 'alkoholu' in search_term: search_term = 'alkoholu'
    if 'narkotykow' in search_term: search_term = 'narkotykow'
    if 'stacjonarna' in search_term: search_term = 'stacjonarna'
    filter_kwargs = {f"{db_field}__icontains": search_term}
    facilities_list = Facility.objects.filter(**filter_kwargs)
    context = {
        'facilities_list': facilities_list,
        'category_name': f"{category_type.replace('-', ' ').title()}: {search_term.title()}",
        'now': timezone.now(),
    }
    return render(request, 'help_section/facility_list.html', context)

def facility_detail_view(request, slug):
    facility = get_object_or_404(Facility, slug=slug)
    comments = facility.comments.filter(is_approved=True)
    rating_categories = RatingCategory.objects.all()

    # Handle forms
    comment_form = CommentForm()
    rating_form = RatingForm()

    if request.method == 'POST':
        # Differentiate between comment and rating form submissions
        if 'submit_comment' in request.POST:
            form = CommentForm(request.POST)
            if form.is_valid():
                test_user = User.objects.first() or User.objects.create_superuser('admin', 'admin@example.com', 'password')
                new_comment = form.save(commit=False)
                new_comment.facility = facility
                new_comment.author = test_user
                new_comment.save()
                return redirect('facility_detail', slug=facility.slug)
        
        elif 'submit_rating' in request.POST:
            form = RatingForm(request.POST)
            if form.is_valid():
                test_user = User.objects.first() or User.objects.create_superuser('admin', 'admin@example.com', 'password')
                for category in rating_categories:
                    if category.slug in form.cleaned_data:
                        FacilityRating.objects.update_or_create(
                            facility=facility,
                            author=test_user,
                            category=category,
                            defaults={'value': form.cleaned_data[category.slug]}
                        )
                return redirect('facility_detail', slug=facility.slug)

    # Calculate average ratings
    average_ratings = FacilityRating.objects.filter(facility=facility).values('category__slug').annotate(average=Avg('value'))
    avg_ratings_dict = {item['category__slug']: item['average'] for item in average_ratings}

    context = {
        'facility': facility,
        'comments': comments,
        'comment_form': comment_form,
        'rating_categories': rating_categories,
        'rating_form': rating_form,
        'average_ratings': avg_ratings_dict,
        'now': timezone.now(),
    }
    
    return render(request, 'help_section/facility_detail.html', context)
