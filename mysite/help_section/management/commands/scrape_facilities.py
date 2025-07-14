import os
import json
import requests # Keep for potential future online fetching, though not used for local files
from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
from help_section.models import Facility # Ensure your model is correctly imported
from urllib.parse import urljoin # For constructing full URLs if needed

# Directory containing the local individual HTML files for facilities
LOCAL_HTML_PLACÓWKI_DIR = 'mysite/hyperreal_old_scrapper/extracted_data/scraped_hyperreal_help_html/placowka/'
# JSON file containing the list of facilities and their original URLs
PLACÓWKI_JSON_FILE = 'mysite/hyperreal_old_scrapper/extracted_data/placowki_data.json'
BASE_HYPERREAL_URL = 'https://hyperreal.info' # Used to construct full URLs from canonical links

class Command(BaseCommand):
    help = 'Scrapes facility data from local HTML files listed in a JSON manifest.'

    def _get_field_text(self, main_node, class_name):
        field_div = main_node.find('div', class_=class_name)
        if field_div:
            items = field_div.find_all('div', class_='field-item')
            if items:
                return ', '.join(item.text.strip() for item in items if item.text.strip())
            field_label_tag = field_div.find('div', class_='field-label')
            field_label_text = field_label_tag.text.strip() if field_label_tag else ""
            item_text = field_div.text.strip().replace(field_label_text, '').strip()
            return item_text if item_text else None
        return None

    def _get_link_field_href(self, main_node, class_name):
        field_div = main_node.find('div', class_=class_name)
        if field_div:
            link_tag = field_div.find('a')
            if link_tag and link_tag.get('href'):
                return link_tag.get('href').strip()
        return None

    def handle(self, *args, **options):
        NL = os.linesep # Define newline character using os.linesep

        self.stdout.write('[SUCCESS] Starting facility scraping process from local HTML files...')

        if not os.path.isfile(PLACÓWKI_JSON_FILE):
            self.stderr.write(f'[ERROR] JSON manifest file not found: {PLACÓWKI_JSON_FILE}')
            return
        
        if not os.path.isdir(LOCAL_HTML_PLACÓWKI_DIR):
            self.stderr.write(f'[ERROR] Directory with local HTML files not found: {LOCAL_HTML_PLACÓWKI_DIR}')
            return

        with open(PLACÓWKI_JSON_FILE, 'r', encoding='utf-8') as f:
            placowki_manifest = json.load(f)

        self.stdout.write(f'[SUCCESS] Loaded {len(placowki_manifest)} facility entries from JSON manifest.')
        processed_count = 0

        for entry in placowki_manifest:
            facility_name_from_json = entry.get('nazwa', 'Brak nazwy w JSON')
            original_url_from_json = entry.get('url_oryginalny_tresci')

            if not original_url_from_json:
                self.stdout.write(f"[WARNING] Skipping entry for '{facility_name_from_json}' due to missing original URL.")
                continue

            # Construct the local HTML file path from the original URL
            url_path_segment = original_url_from_json.split('/placowka/')[-1]
            local_html_filename = f"{url_path_segment}.html"
            local_html_filepath = os.path.join(LOCAL_HTML_PLACÓWKI_DIR, local_html_filename)

            self.stdout.write(f"Processing: {facility_name_from_json} (URL: {original_url_from_json})")
            self.stdout.write(f"  Expected local HTML: {local_html_filepath}")

            if not os.path.isfile(local_html_filepath):
                self.stdout.write(f'[WARNING]   Local HTML file not found: {local_html_filepath}. Skipping.')
                continue

            try:
                with open(local_html_filepath, 'r', encoding='utf-8') as f_html:
                    html_content = f_html.read()
                detail_soup = BeautifulSoup(html_content, 'html.parser')
            except Exception as e:
                self.stderr.write(f'[ERROR]   Error reading or parsing local HTML file {local_html_filepath}: {e}')
                continue
            
            canonical_link_tag = detail_soup.find('link', rel='canonical', href=True)
            hyperreal_link_for_db = original_url_from_json 
            if canonical_link_tag:
                canonical_href = getattr(canonical_link_tag, 'get', lambda x, y=None: None)('href', None)
                if isinstance(canonical_href, str):
                    hyperreal_link_for_db = urljoin(BASE_HYPERREAL_URL, canonical_href)
                else:
                    self.stdout.write(f"[WARNING]    Canonical link in {local_html_filepath} is not a string, using URL from JSON.")
            else:
                self.stdout.write(f"[WARNING]    Canonical link not found in {local_html_filepath}, using URL from JSON.")

            defaults_for_db = {}
            try:
                existing_facility = Facility.objects.get(hyperreal_link=hyperreal_link_for_db)
                for field in Facility._meta.get_fields():
                    if hasattr(field, 'attname') and field.attname not in ['id', 'slug', 'created_at', 'updated_at']:
                        defaults_for_db[field.attname] = getattr(existing_facility, field.attname, None)
            except Facility.DoesNotExist:
                pass
            
            defaults_for_db['name'] = facility_name_from_json

            main_content_node = detail_soup.find('div', class_=['node', 'node-osrodek', 'view-mode-full'])
            if main_content_node:
                full_address_text = self._get_field_text(main_content_node, 'field-name-field-adres')
                if full_address_text: defaults_for_db['full_address_text_detail'] = full_address_text

                phone_text = self._get_field_text(main_content_node, ['field-name-field-telefon-stacjonarny', 'field-name-field-telefon'])
                if phone_text: defaults_for_db['phone_number'] = phone_text

                email_text_raw = self._get_field_text(main_content_node, 'field-name-field-email')
                if email_text_raw:
                    email_div = main_content_node.find('div', class_='field-name-field-email')
                    email_link = email_div.find('a') if email_div else None
                    if email_link and email_link.get('href','').startswith('mailto:'):
                        defaults_for_db['email'] = email_link.text.strip()
                    else: 
                        defaults_for_db['email'] = email_text_raw

                website_url = self._get_link_field_href(main_content_node, ['field-name-field-adres-strony-www', 'field-name-field-www'])
                if website_url: defaults_for_db['website'] = website_url
                
                voivodeship_text = self._get_field_text(main_content_node, 'field-name-field-wojewodztwo')
                if voivodeship_text: defaults_for_db['voivodeship'] = voivodeship_text
                
                places_text = self._get_field_text(main_content_node, 'field-name-field-ilosc-miejsc')
                if places_text and places_text.isdigit(): defaults_for_db['number_of_places'] = int(places_text)
                
                defaults_for_db['addiction_types_text'] = self._get_field_text(main_content_node, 'field-name-field-rodzaje-uzaleznien') or defaults_for_db.get('addiction_types_text',"")
                defaults_for_db['program_lengths_text'] = self._get_field_text(main_content_node, 'field-name-field-dlugosc-programu') or defaults_for_db.get('program_lengths_text',"")
                defaults_for_db['therapy_types_text'] = self._get_field_text(main_content_node, 'field-name-field-rodzaj-terapii') or defaults_for_db.get('therapy_types_text',"")
                defaults_for_db['facility_type_text'] = self._get_field_text(main_content_node, 'field-name-field-typ-placowki') or defaults_for_db.get('facility_type_text',"")
                defaults_for_db['psychotherapy_types_text'] = self._get_field_text(main_content_node, 'field-name-field-psychoterapia') or defaults_for_db.get('psychotherapy_types_text',"")
                defaults_for_db['counseling_types_text'] = self._get_field_text(main_content_node, 'field-name-field-poradnictwo') or defaults_for_db.get('counseling_types_text',"")
                defaults_for_db['other_activities_text'] = self._get_field_text(main_content_node, 'field-name-field-inne-dzialania') or defaults_for_db.get('other_activities_text',"")
                defaults_for_db['last_updated_hyperreal_text'] = self._get_field_text(main_content_node, 'field-name-changed-date') or defaults_for_db.get('last_updated_hyperreal_text',"")
            else:
                self.stdout.write(f"[WARNING]    Could not find main content node in local HTML file: {local_html_filepath}")

            if not defaults_for_db.get('name'):
                title_tag = detail_soup.find('title')
                if title_tag:
                    defaults_for_db['name'] = title_tag.text.split('|')[0].strip()
                if not defaults_for_db.get('name'): 
                    self.stderr.write(f'[ERROR]  CRITICAL: Cannot save facility, name is missing for {hyperreal_link_for_db}')
                    continue
            
            try:
                facility, created = Facility.objects.update_or_create(
                    hyperreal_link=hyperreal_link_for_db,
                    defaults=defaults_for_db
                )
                processed_count +=1
                if created:
                    self.stdout.write(f'[SUCCESS]  Successfully CREATED facility: {defaults_for_db["name"]}')
                else:
                    self.stdout.write(f'[SUCCESS]  Successfully UPDATED facility: {defaults_for_db["name"]}')
            except Exception as e_db:
                 self.stderr.write(f'[ERROR]  Error saving facility {defaults_for_db.get("name", original_url_from_json)} to DB: {e_db}')

            self.stdout.write("  ---")
        
        self.stdout.write(f'[SUCCESS] Scraping process finished. Processed {processed_count} facilities.')
