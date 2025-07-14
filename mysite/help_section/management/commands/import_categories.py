from django.core.management.base import BaseCommand
from help_section.models import AddictionType, FacilityType, Voivodeship, ProgramLength, TherapyType, PsychotherapyType, CounselingType, LegalIssue, AdditionalActivity, AgeGenderGroup
from django.utils.text import slugify
import os
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
HTML_BASE = os.path.join(BASE_DIR, 'hyperreal_old_scrapper', 'extracted_data', 'scraped_hyperreal_help_html')

CATEGORIES = [
    ('rodzaj_uzaleznien', AddictionType),
    ('typ_placowki', FacilityType),
    ('wojewodztwo', Voivodeship),
    ('dlugosc_programu', ProgramLength),
    ('rodzaj_terapii', TherapyType),
    ('psychoterapia', PsychotherapyType),
    ('poradnictwo', CounselingType),
    ('dzialania_zwiazane_z_klopotami_z_prawem', LegalIssue),
    ('dzialania_dodatkowe', AdditionalActivity),
    ('grupa_wiekowa_i_plec', AgeGenderGroup),
]

class Command(BaseCommand):
    help = 'Importuje kategorie (rodzaje uzależnień, typy placówek, województwa) z lokalnych plików HTML.'

    def handle(self, *args, **options):
        for folder, model in CATEGORIES:
            dir_path = os.path.join(HTML_BASE, folder)
            if not os.path.isdir(dir_path):
                self.stdout.write(f'[WARNING] Brak katalogu: {dir_path}')
                continue
            for fname in os.listdir(dir_path):
                if not fname.endswith('.html'):
                    continue
                fpath = os.path.join(dir_path, fname)
                with open(fpath, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f, 'html.parser')
                    # Nazwa kategorii z tytułu strony lub pliku
                    if soup.title and soup.title.string:
                        title = soup.title.string.strip()
                    else:
                        title = os.path.splitext(fname)[0]
                    slug = slugify(title)
                    obj, created = model.objects.get_or_create(slug=slug, defaults={'name': title})
                    if created:
                        self.stdout.write(f'[SUCCESS] Utworzono: {model.__name__} - {title}')
                    else:
                        self.stdout.write(f'Istnieje: {model.__name__} - {title}')
        self.stdout.write('[SUCCESS] Import kategorii zakończony.') 