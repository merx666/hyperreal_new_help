from django.core.management.base import BaseCommand
from help_section.models import Facility, AddictionType, FacilityType, Voivodeship, ProgramLength, TherapyType, PsychotherapyType, CounselingType, LegalIssue, AdditionalActivity, AgeGenderGroup
from django.db import transaction

def assign_m2m(facility, model, m2m_field, text_value):
    if not text_value:
        return
    # Rozbij tekst po przecinkach, średnikach, enterach
    items = [i.strip().lower() for i in text_value.replace('\n', ',').replace(';', ',').split(',') if i.strip()]
    for item in items:
        # Szukaj po name (case-insensitive)
        obj = model.objects.filter(name__iexact=item).first()
        if obj:
            getattr(facility, m2m_field).add(obj)

class Command(BaseCommand):
    help = 'Przypisuje kategorie many-to-many do placówek na podstawie pól tekstowych.'

    @transaction.atomic
    def handle(self, *args, **options):
        facilities = Facility.objects.all()
        for facility in facilities:
            # Czyść stare powiązania
            facility.addiction_types.clear()
            facility.facility_types.clear()
            facility.voivodeships.clear()
            facility.program_lengths.clear()
            facility.therapy_types.clear()
            facility.psychotherapy_types.clear()
            facility.counseling_types.clear()
            facility.legal_issues.clear()
            facility.other_actions.clear()
            facility.age_gender_groups.clear()
            # Przypisz na podstawie tekstów
            assign_m2m(facility, AddictionType, 'addiction_types', facility.addiction_types_text)
            assign_m2m(facility, FacilityType, 'facility_types', facility.facility_type_text)
            assign_m2m(facility, Voivodeship, 'voivodeships', facility.voivodeship)
            assign_m2m(facility, ProgramLength, 'program_lengths', facility.program_lengths_text)
            assign_m2m(facility, TherapyType, 'therapy_types', facility.therapy_types_text)
            assign_m2m(facility, PsychotherapyType, 'psychotherapy_types', facility.psychotherapy_types_text)
            assign_m2m(facility, CounselingType, 'counseling_types', facility.counseling_types_text)
            assign_m2m(facility, LegalIssue, 'legal_issues', facility.other_activities_text)
            assign_m2m(facility, AdditionalActivity, 'other_actions', facility.other_activities_text)
            assign_m2m(facility, AgeGenderGroup, 'age_gender_groups', facility.other_activities_text)
            facility.save()
            self.stdout.write(f'Przypisano kategorie do: {facility.name}')
        self.stdout.write('[SUCCESS] Przypisywanie kategorii zakończone.') 