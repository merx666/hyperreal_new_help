from django.core.management.base import BaseCommand
from help_section.models import Facility, AddictionType, FacilityType, Voivodeship, ProgramLength, TherapyType, PsychotherapyType, CounselingType, LegalIssue, AdditionalActivity, AgeGenderGroup
from django.db import transaction
import os
from bs4 import BeautifulSoup, Tag
import re
from django.utils.text import slugify

# Ścieżka do katalogu z HTML
HTML_BASE = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            )
        )
    ),
    'hyperreal_old_scrapper',
    'extracted_data',
    'scraped_hyperreal_help_html'
)

# Mapowanie kategorii na foldery i modele
CATEGORY_MAP = [
    ('grupa_wiekowa', AgeGenderGroup),
    ('grupa_wiekowa_i_plec', AgeGenderGroup),
    ('typ_placowki', FacilityType),
    ('rodzaj_uzaleznien', AddictionType),
    ('rodzaj_terapii', TherapyType),
    ('psychoterapia', PsychotherapyType),
    ('poradnictwo', CounselingType),
    ('dzialania_zwiazane_z_klopotami_z_prawem', LegalIssue),
    ('dzialania_dodatkowe', AdditionalActivity),
    ('wojewodztwo', Voivodeship),
    ('dlugosc_programu', ProgramLength),
]

# Mapowanie modelu na nazwę pola many-to-many w Facility
MODEL_TO_FIELD = {
    AddictionType: 'addiction_types',
    FacilityType: 'facility_types',
    Voivodeship: 'voivodeships',
    ProgramLength: 'program_lengths',
    TherapyType: 'therapy_types',
    PsychotherapyType: 'psychotherapy_types',
    CounselingType: 'counseling_types',
    LegalIssue: 'legal_issues',
    AdditionalActivity: 'other_actions',
    AgeGenderGroup: 'age_gender_groups',
}

# Pomocnicza funkcja do normalizacji nazw placówek

def normalize_name(name):
    return re.sub(r'\s+', ' ', name.strip().lower().replace('„','').replace('”','').replace('"',''))

FILTERED_LINK_TEXTS = [
    'Czytaj dalej', 'nast.', 'ostatnia', 'poprzednia', 'pierwsza', 'więcej', 'zobacz więcej', 'czytaj więcej'
]

class Command(BaseCommand):
    help = 'Importuje WSZYSTKIE kategorie i powiązania placówek z HTML starej strony.'

    def handle(self, *args, **options):
        errors = []
        imported_links = 0
        for folder, model in CATEGORY_MAP:
            folder_path = os.path.join(HTML_BASE, folder)
            if not os.path.isdir(folder_path):
                continue
            for fname in os.listdir(folder_path):
                if not fname.endswith('.html'):
                    continue
                fpath = os.path.join(folder_path, fname)
                with open(fpath, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                # Nazwa kategorii = h1 lub title
                h1 = soup.find('h1')
                if not h1:
                    continue
                cat_name = h1.get_text(strip=True)
                # Znajdź kategorię po nazwie lub utwórz
                # cat_obj, _ = model.objects.get_or_create(name__icontains=cat_name, defaults={'name': cat_name, 'slug': fname.replace('.html','')})
                # Szukaj linków do placówek
                facilities = Facility.objects.all()
                for a in soup.find_all('a', href=True):
                    if not isinstance(a, Tag):
                        continue
                    href = a.attrs.get('href', '')
                    plac_name = a.get_text(strip=True)
                    # Pomijaj linki nawigacyjne/paginacyjne i placówki o nazwie będącej liczbą
                    if not plac_name or any(txt.lower() in plac_name.lower() for txt in FILTERED_LINK_TEXTS) or plac_name.isdigit():
                        continue
                    if isinstance(href, str) and ('/help/placowka/' in href or href.startswith('/help/placowka/') or 'placowka_' in href):
                        # Normalizuj nazwę
                        norm = normalize_name(plac_name)
                        plac = None
                        for f in facilities:
                            if normalize_name(f.name) == norm:
                                plac = f
                                break
                        if not plac:
                            self.stdout.write(f'Nie znaleziono placówki: {plac_name}')
                            continue
                        field_name = MODEL_TO_FIELD[model]
                        # Szukaj kategorii: slug, exact name, icontains (ale tylko jeśli jedna)
                        cat_obj = None
                        cat_slug_norm = slugify(cat_name)
                        try:
                            cat_obj = model.objects.get(slug=cat_slug_norm)
                        except model.DoesNotExist:
                            try:
                                cat_obj = model.objects.get(name__iexact=cat_name)
                            except model.MultipleObjectsReturned:
                                self.stdout.write(f'Wiele kategorii dla: {cat_name} (slug: {cat_slug_norm}) – pomijam')
                                continue
                            except model.DoesNotExist:
                                qs = model.objects.filter(name__icontains=cat_name)
                                if qs.count() == 1:
                                    cat_obj = qs.first()
                                elif qs.count() > 1:
                                    self.stdout.write(f'Wiele kategorii (icontains) dla: {cat_name} (slug: {cat_slug_norm}) – pomijam')
                                    continue
                                else:
                                    self.stdout.write(f'Nie znaleziono kategorii: {cat_name} (slug: {cat_slug_norm})')
                                    continue
                        except model.MultipleObjectsReturned:
                            self.stdout.write(f'Wiele kategorii dla: {cat_name} (slug: {cat_slug_norm}) – pomijam')
                            continue
                        getattr(plac, field_name).add(cat_obj)
                        imported_links += 1
        self.stdout.write(f'Zaimportowano {imported_links} powiązań placówek z kategoriami.')
        if errors:
            self.stdout.write(f'Błędy ({len(errors)}):')
            for e in errors:
                self.stdout.write(e)
        else:
            self.stdout.write('Brak błędów!') 