from django.core.management.base import BaseCommand
from help_section.models import AgeGenderGroup

CATEGORIES = [
    ("Placówka adresowana tylko do dorosłych", "placowka-adresowana-tylko-do-doroslych-hyperreal-help-chcemy-pomoc"),
    ("Placówka adresowana tylko do młodzieży", "placowka-adresowana-tylko-do-mlodziezy-hyperreal-help-chcemy-pomoc"),
    ("Placówka adresowana zarówno do młodzieży jak i dorosłych", "placowka-adresowana-zarowno-do-mlodziezy-jak-i-doroslych-hyperreal-help-chcemy-pomoc"),
    ("Placówka przyjmuje uzależnione matki z dziećmi | Hyperreal [H]elp - chcemy pomóc", "placowka-przyjmuje-uzaleznione-matki-z-dziecmi-hyperreal-help-chcemy-pomoc"),
    ("Placówka adresowana tylko do mężczyzn | Hyperreal [H]elp - chcemy pomóc", "placowka-adresowana-tylko-do-mezczyzn-hyperreal-help-chcemy-pomoc"),
    ("Placówka adresowana tylko do kobiet | Hyperreal [H]elp - chcemy pomóc", "placowka-adresowana-tylko-do-kobiet-hyperreal-help-chcemy-pomoc"),
]

class Command(BaseCommand):
    help = "Create or update AgeGenderGroup categories with correct slugs."

    def handle(self, *args, **options):
        for name, slug in CATEGORIES:
            obj, created = AgeGenderGroup.objects.get_or_create(slug=slug, defaults={"name": name})
            if not created and obj.name != name:
                obj.name = name
                obj.save()
            self.stdout.write(self.style.SUCCESS(f"{'Created' if created else 'Updated'}: {name} ({slug})")) 