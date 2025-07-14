from django.core.management.base import BaseCommand
from django.db import transaction
from bs4 import BeautifulSoup
import os
import re
from help_section.models import Facility, AddictionType, FacilityType, Voivodeship, ProgramLength, TherapyType, PsychotherapyType, CounselingType, AdditionalActivity, LegalIssue, AgeGenderGroup

class Command(BaseCommand):
    help = 'Import facility details from HTML files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--html-dir',
            type=str,
            default='mysite/hyperreal_old_scrapper/extracted_data/scraped_hyperreal_help_html/placowka',
            help='Directory containing HTML files'
        )

    def handle(self, *args, **options):
        html_dir = options['html_dir']
        
        if not os.path.exists(html_dir):
            self.stdout.write(self.style.ERROR(f'Directory {html_dir} does not exist'))
            return

        html_files = [f for f in os.listdir(html_dir) if f.endswith('.html')]
        self.stdout.write(f'Found {len(html_files)} HTML files to process')

        imported_count = 0
        updated_count = 0

        for html_file in html_files:
            try:
                file_path = os.path.join(html_dir, html_file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()

                # Parse HTML
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Extract facility name from title
                title = soup.find('title')
                if not title:
                    continue
                
                title_text = title.get_text()
                facility_name = title_text.split(' | ')[0].strip()
                
                # Try to find existing facility by name
                facility = None
                try:
                    facility = Facility.objects.get(name__icontains=facility_name)
                except Facility.DoesNotExist:
                    # Try partial match
                    for existing_facility in Facility.objects.all():
                        if facility_name.lower() in existing_facility.name.lower() or existing_facility.name.lower() in facility_name.lower():
                            facility = existing_facility
                            break

                if not facility:
                    self.stdout.write(f'Could not find facility: {facility_name}')
                    continue

                # Extract contact information
                contact_info = self.extract_contact_info(soup)
                
                # Extract categories
                categories = self.extract_categories(soup)
                
                # Update facility
                with transaction.atomic():
                    # Update basic info
                    if contact_info.get('address'):
                        facility.full_address_text_detail = contact_info['address']
                    if contact_info.get('phone'):
                        facility.phone_number = contact_info['phone']
                    if contact_info.get('email'):
                        facility.email = contact_info['email']
                    if contact_info.get('website'):
                        facility.website = contact_info['website']
                    if contact_info.get('places_count'):
                        facility.number_of_places = contact_info['places_count']
                    
                    facility.save()
                    
                    # Clear existing categories and add new ones
                    facility.addiction_types.clear()
                    facility.facility_types.clear()
                    facility.voivodeships.clear()
                    facility.program_lengths.clear()
                    facility.therapy_types.clear()
                    facility.psychotherapy_types.clear()
                    facility.counseling_types.clear()
                    facility.other_actions.clear()
                    facility.legal_issues.clear()
                    facility.age_gender_groups.clear()
                    
                    # Add categories
                    for addiction_type in categories.get('addiction_types', []):
                        facility.addiction_types.add(addiction_type)
                    
                    for facility_type in categories.get('facility_types', []):
                        facility.facility_types.add(facility_type)
                    
                    for voivodeship in categories.get('voivodeships', []):
                        facility.voivodeships.add(voivodeship)
                    
                    for program_length in categories.get('program_lengths', []):
                        facility.program_lengths.add(program_length)
                    
                    for therapy_type in categories.get('therapy_types', []):
                        facility.therapy_types.add(therapy_type)
                    
                    for psychotherapy in categories.get('psychotherapies', []):
                        facility.psychotherapy_types.add(psychotherapy)
                    
                    for counseling in categories.get('counselings', []):
                        facility.counseling_types.add(counseling)
                    
                    for action in categories.get('additional_actions', []):
                        facility.other_actions.add(action)
                    
                    for legal_issue in categories.get('legal_issues', []):
                        facility.legal_issues.add(legal_issue)
                    
                    for age_gender_group in categories.get('age_gender_groups', []):
                        facility.age_gender_groups.add(age_gender_group)

                updated_count += 1
                self.stdout.write(f'Updated: {facility_name}')

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing {html_file}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_count} facilities'))

    def extract_contact_info(self, soup):
        """Extract contact information from HTML"""
        info = {}
        
        # Find all field items
        field_items = soup.find_all('div', class_='field-item')
        
        for item in field_items:
            # Get the parent field to understand what type of data this is
            parent_field = item.find_parent('div', class_='field')
            if not parent_field:
                continue
                
            field_label = parent_field.find('div', class_='field-label')
            if not field_label:
                continue
                
            label_text = field_label.get_text().strip().lower()
            item_text = item.get_text().strip()
            
            if 'adres:' in label_text:
                info['address'] = item_text
            elif 'telefon' in label_text:
                info['phone'] = item_text
            elif 'email:' in label_text:
                info['email'] = item_text
            elif 'www' in label_text or 'strona' in label_text:
                # Extract URL from link
                link = item.find('a')
                if link:
                    info['website'] = link.get('href', '')
                else:
                    info['website'] = item_text
            elif 'miejsc' in label_text:
                # Extract number from text
                numbers = re.findall(r'\d+', item_text)
                if numbers:
                    info['places_count'] = int(numbers[0])
        
        return info

    def extract_categories(self, soup):
        """Extract categories from HTML"""
        categories = {
            'addiction_types': [],
            'facility_types': [],
            'voivodeships': [],
            'program_lengths': [],
            'therapy_types': [],
            'psychotherapies': [],
            'counselings': [],
            'additional_actions': [],
            'legal_issues': [],
            'age_gender_groups': []
        }
        
        # Find all field items with links
        field_items = soup.find_all('div', class_='field-item')
        
        for item in field_items:
            links = item.find_all('a')
            if not links:
                continue
                
            parent_field = item.find_parent('div', class_='field')
            if not parent_field:
                continue
                
            field_label = parent_field.find('div', class_='field-label')
            if not field_label:
                continue
                
            label_text = field_label.get_text().strip().lower()
            
            for link in links:
                href = link.get('href', '')
                link_text = link.get_text().strip()
                
                # Map categories based on URL patterns and labels
                if 'uzaleznien' in label_text:
                    if 'alkoholu' in link_text.lower():
                        categories['addiction_types'].extend(
                            AddictionType.objects.filter(name__icontains='alkohol')
                        )
                    elif 'narkotyk' in link_text.lower():
                        categories['addiction_types'].extend(
                            AddictionType.objects.filter(name__icontains='narkotyk')
                        )
                
                elif 'typ placowki' in label_text:
                    categories['facility_types'].extend(
                        FacilityType.objects.filter(name__icontains=link_text)
                    )
                
                elif 'wojewodztwo' in label_text:
                    categories['voivodeships'].extend(
                        Voivodeship.objects.filter(name__icontains=link_text)
                    )
                
                elif 'dlugosc' in label_text:
                    if 'krotko' in link_text.lower():
                        categories['program_lengths'].extend(
                            ProgramLength.objects.filter(name__icontains='krótko')
                        )
                    elif 'srednio' in link_text.lower():
                        categories['program_lengths'].extend(
                            ProgramLength.objects.filter(name__icontains='średnio')
                        )
                    elif 'dlugo' in link_text.lower():
                        categories['program_lengths'].extend(
                            ProgramLength.objects.filter(name__icontains='długo')
                        )
                
                elif 'rodzaj terapii' in label_text:
                    categories['therapy_types'].extend(
                        TherapyType.objects.filter(name__icontains=link_text)
                    )
                
                elif 'psychoterapia' in label_text:
                    categories['psychotherapies'].extend(
                        PsychotherapyType.objects.filter(name__icontains=link_text)
                    )
                
                elif 'poradnictwo' in label_text:
                    categories['counselings'].extend(
                        CounselingType.objects.filter(name__icontains=link_text)
                    )
                
                elif 'inne dzialania' in label_text or 'dodatkowe' in label_text:
                    categories['additional_actions'].extend(
                        AdditionalActivity.objects.filter(name__icontains=link_text)
                    )
                
                elif 'praw' in label_text or 'sad' in label_text:
                    categories['legal_issues'].extend(
                        LegalIssue.objects.filter(name__icontains=link_text)
                    )
                
                elif 'wiek' in label_text or 'plec' in label_text:
                    categories['age_gender_groups'].extend(
                        AgeGenderGroup.objects.filter(name__icontains=link_text)
                    )
        
        return categories 