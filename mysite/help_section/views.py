from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Avg, Q, Count
from .models import Facility, Comment, RatingCategory, FacilityRating
from .forms import CommentForm, RatingForm
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

def help_view(request):
    now = timezone.now()
    context = {'now': now}
    return render(request, 'help_section/help_page.html', context)

def facility_categories_view(request):
    now = timezone.now()
    context = {'now': now}
    return render(request, 'help_section/facility_categories.html', context)

def search_facilities(request):
    query = request.GET.get('q', '')
    voivodeship = request.GET.get('voivodeship', '')
    addiction_type = request.GET.get('addiction_type', '')
    facility_type = request.GET.get('facility_type', '')
    sort_by = request.GET.get('sort', 'name')
    
    facilities = Facility.objects.all()
    
    # Filtry
    if query:
        facilities = facilities.filter(
            Q(name__icontains=query) |
            Q(full_address_text_detail__icontains=query) |
            Q(description__icontains=query) |
            Q(voivodeship__icontains=query) |
            Q(addiction_types_text__icontains=query) |
            Q(facility_type_text__icontains=query)
        )
    
    if voivodeship:
        facilities = facilities.filter(voivodeships__name__icontains=voivodeship)
    
    if addiction_type:
        facilities = facilities.filter(addiction_types__name__icontains=addiction_type)
    
    if facility_type:
        facilities = facilities.filter(facility_types__name__icontains=facility_type)
    
    # Sortowanie
    if sort_by == 'name':
        facilities = facilities.order_by('name')
    elif sort_by == 'voivodeship':
        facilities = facilities.order_by('voivodeship', 'name')
    elif sort_by == 'type':
        facilities = facilities.order_by('facility_type_text', 'name')
    
    facilities = facilities.distinct()
    
    # Pobierz dostępne opcje dla filtrów
    from .models import Voivodeship, AddictionType, FacilityType
    
    voivodeships = Voivodeship.objects.all().order_by('name')
    addiction_types = AddictionType.objects.all().order_by('name')
    facility_types = FacilityType.objects.all().order_by('name')
    
    context = {
        'facilities': facilities,
        'query': query,
        'voivodeship': voivodeship,
        'addiction_type': addiction_type,
        'facility_type': facility_type,
        'sort_by': sort_by,
        'voivodeships': voivodeships,
        'addiction_types': addiction_types,
        'facility_types': facility_types,
        'now': timezone.now(),
    }
    return render(request, 'help_section/search_results.html', context)

def facility_list_alphabetical(request, letter=None):
    if letter:
        # Filtruj placówki zaczynające się od danej litery
        facilities = Facility.objects.filter(name__istartswith=letter).order_by('name')
    else:
        # Wszystkie placówki
        facilities = Facility.objects.all().order_by('name')
    
    # Generuj alfabet z liczbą placówek na literę
    alphabet = {}
    for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        count = Facility.objects.filter(name__istartswith=char).count()
        if count > 0:
            alphabet[char] = count
    
    context = {
        'facilities': facilities,
        'alphabet': alphabet,
        'current_letter': letter,
        'now': timezone.now(),
    }
    return render(request, 'help_section/facility_list_alphabetical.html', context)

def facility_list_by_category(request, category_type, category_slug):
    from django.http import Http404
    
    # Mapowanie typów kategorii na modele i pola
    category_mapping = {
        'rodzaj-uzaleznien': {
            'model': 'addiction_types',
            'field': 'slug',
            'name_field': 'name'
        },
        'typ-placowki': {
            'model': 'facility_types', 
            'field': 'slug',
            'name_field': 'name'
        },
        'wojewodztwo': {
            'model': 'voivodeships',
            'field': 'slug', 
            'name_field': 'name'
        },
        'grupa-wiekowa-plec': {
            'model': 'age_gender_groups',
            'field': 'slug',
            'name_field': 'name'
        },
        'rodzaj-leczenia': {
            'model': 'other_actions',
            'field': 'slug',
            'name_field': 'name'
        },
        'dlugosc-programu': {
            'model': 'program_lengths',
            'field': 'slug',
            'name_field': 'name'
        },
        'rodzaj-terapii': {
            'model': 'therapy_types',
            'field': 'slug',
            'name_field': 'name'
        },
        'poradnictwo': {
            'model': 'counseling_types',
            'field': 'slug',
            'name_field': 'name'
        },
        'psychoterapia': {
            'model': 'psychotherapy_types',
            'field': 'slug',
            'name_field': 'name'
        },
        'dzialania-prawne': {
            'model': 'legal_issues',
            'field': 'slug',
            'name_field': 'name'
        },
        'inne-dzialania': {
            'model': 'other_actions',
            'field': 'slug',
            'name_field': 'name'
        },
    }
    
    category_config = category_mapping.get(category_type)
    if not category_config:
        raise Http404("Nieznany typ kategorii.")
    
    # Pobierz kategorię
    from .models import (
        AddictionType, FacilityType, Voivodeship, AgeGenderGroup, 
        ProgramLength, TherapyType, CounselingType, PsychotherapyType,
        LegalIssue, AdditionalActivity
    )
    
    model_map = {
        'addiction_types': AddictionType,
        'facility_types': FacilityType,
        'voivodeships': Voivodeship,
        'age_gender_groups': AgeGenderGroup,
        'program_lengths': ProgramLength,
        'therapy_types': TherapyType,
        'counseling_types': CounselingType,
        'psychotherapy_types': PsychotherapyType,
        'legal_issues': LegalIssue,
        'other_actions': AdditionalActivity,
    }
    
    category_model = model_map.get(category_config['model'])
    if not category_model:
        raise Http404("Nieznany model kategorii.")
    
    try:
        category = category_model.objects.get(slug=category_slug)
    except category_model.DoesNotExist:
        raise Http404("Kategoria nie istnieje.")
    
    # Pobierz placówki z tą kategorią
    filter_kwargs = {f"{category_config['model']}": category}
    facilities_list = Facility.objects.filter(**filter_kwargs).distinct()
    
    context = {
        'facilities_list': facilities_list,
        'category_name': f"{category_type.replace('-', ' ').title()}: {getattr(category, category_config['name_field'])}",
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

def facility_map_view(request):
    facilities = Facility.objects.all()
    
    context = {
        'facilities': facilities,
        'now': timezone.now(),
    }
    return render(request, 'help_section/facility_map.html', context)

def facility_map_data(request):
    """API endpoint zwracający dane placówek w formacie JSON dla mapy"""
    from django.http import JsonResponse
    
    facilities = Facility.objects.all()
    facilities_data = []
    
    for facility in facilities:
        # Pobierz kategorie dla tej placówki
        addiction_types = [at.name for at in facility.addiction_types.all()]
        facility_types = [ft.name for ft in facility.facility_types.all()]
        voivodeships = [v.name for v in facility.voivodeships.all()]
        
        facility_data = {
            'id': facility.id,
            'name': facility.name,
            'slug': facility.slug,
            'address_city': facility.address_city,
            'address_street': facility.address_street,
            'phone_number': facility.phone_number,
            'email': facility.email,
            'website': facility.website,
            'description': facility.description[:200] + '...' if facility.description and len(facility.description) > 200 else facility.description,
            'latitude': float(facility.latitude) if facility.latitude else None,
            'longitude': float(facility.longitude) if facility.longitude else None,
            'addiction_types': addiction_types,
            'facility_types': facility_types,
            'voivodeships': voivodeships,
        }
        facilities_data.append(facility_data)
    
    return JsonResponse({'facilities': facilities_data})

def top_rated_facilities(request):
    """Widok najlepszych placówek według ocen"""
    from django.db.models import Avg, Count
    
    # Pobierz placówki z ocenami, posortowane według średniej oceny
    facilities_with_ratings = Facility.objects.annotate(
        avg_rating=Avg('ratings__value'),
        rating_count=Count('ratings')
    ).filter(
        rating_count__gt=0  # Tylko placówki z ocenami
    ).order_by('-avg_rating', '-rating_count')
    
    # Pobierz kategorie ocen
    rating_categories = RatingCategory.objects.all()
    
    context = {
        'facilities': facilities_with_ratings,
        'rating_categories': rating_categories,
        'now': timezone.now(),
    }
    return render(request, 'help_section/top_rated_facilities.html', context)

def newsletter_subscribe(request):
    """Widok do zapisywania się na newsletter"""
    from django.http import JsonResponse
    from .models import Newsletter
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip()
            
            if not email:
                return JsonResponse({'success': False, 'message': 'Adres e-mail jest wymagany.'})
            
            # Sprawdź czy email już istnieje
            if Newsletter.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'message': 'Ten adres e-mail jest już zapisany.'})
            
            # Zapisz nowy email
            Newsletter.objects.create(email=email)
            
            return JsonResponse({'success': True, 'message': 'Dziękujemy za zapisanie się na newsletter!'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Wystąpił błąd. Spróbuj ponownie.'})
    
    return JsonResponse({'success': False, 'message': 'Nieprawidłowa metoda żądania.'})

def faq_view(request):
    """Widok FAQ"""
    faq_data = [
        {
            'question': 'Jak znaleźć odpowiednią placówkę?',
            'answer': 'Możesz użyć wyszukiwania zaawansowanego, przeglądać kategorie placówek lub sprawdzić mapę. Każda placówka ma szczegółowe informacje o oferowanych usługach.'
        },
        {
            'question': 'Czy wszystkie placówki są bezpłatne?',
            'answer': 'Nie, niektóre placówki mogą być płatne. Szczegółowe informacje o kosztach znajdziesz w opisie każdej placówki lub możesz skontaktować się z nimi bezpośrednio.'
        },
        {
            'question': 'Jak mogę ocenić placówkę?',
            'answer': 'Po odwiedzeniu strony szczegółów placówki, możesz dodać swoją ocenę w różnych kategoriach oraz komentarz. Twoja opinia pomoże innym użytkownikom.'
        },
        {
            'question': 'Czy mogę dodać nową placówkę?',
            'answer': 'Obecnie dodawanie placówek jest możliwe tylko przez administratorów. Jeśli znasz placówkę, która powinna być w bazie, skontaktuj się z nami.'
        },
        {
            'question': 'Jak działają filtry w wyszukiwaniu?',
            'answer': 'Możesz filtrować placówki według województwa, typu uzależnienia, typu placówki i innych kryteriów. Filtry można łączyć, aby zawęzić wyniki.'
        },
        {
            'question': 'Czy dane placówek są aktualne?',
            'answer': 'Staramy się utrzymywać dane w aktualnym stanie, ale zalecamy weryfikację informacji bezpośrednio z placówką przed wizytą.'
        }
    ]
    
    context = {
        'faq_data': faq_data,
        'now': timezone.now(),
    }
    return render(request, 'help_section/faq.html', context)

@csrf_exempt
@require_POST
def chatbot_api(request):
    try:
        data = json.loads(request.body)
        question = data.get('question', '').lower()
    except Exception:
        return JsonResponse({'answer': 'Błąd: nieprawidłowe dane wejściowe.'}, status=400)

    # Prosta logika: szukaj słów kluczowych
    keywords = ['alkohol', 'narkotyk', 'detoks', 'warszawa', 'pomoc', 'hostel', 'poradnia', 'leczenie']
    found = []
    for kw in keywords:
        if kw in question:
            # Szukaj placówek po nazwie lub opisie
            facilities = Facility.objects.filter(name__icontains=kw)[:5]
            if not facilities:
                facilities = Facility.objects.filter(description__icontains=kw)[:5]
            if facilities:
                found = facilities
                break
    if found:
        answer = 'Znalazłem następujące placówki:\n'
        for f in found:
            answer += f'- {f.name} ({f.address_city})\n'
    else:
        answer = 'Nie znalazłem odpowiedzi na Twoje pytanie. Spróbuj inaczej lub zapytaj o konkretny typ placówki, miasto lub problem.'
    return JsonResponse({'answer': answer})
