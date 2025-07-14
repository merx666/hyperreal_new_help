from django.core.management.base import BaseCommand
from help_section.models import RatingCategory
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Creates default rating categories.'

    def handle(self, *args, **options):
        rating_categories = [
            {'name': 'Baza materialna', 'description': 'ocena położenia placówki, komfortu zakwaterowania...'},
            {'name': 'Ocena kadry', 'description': 'ocena profesjonalizmu, kompetencji...'},
            {'name': 'Jakość pomocy', 'description': 'ocena wartości oferowanych form pomocy...'},
            {'name': 'Zasady i wymagania', 'description': 'czy obowiązujące zasady są sensowne...'},
            {'name': 'Atmosfera', 'description': 'najbardziej subiektywna z kategorii...'},
        ]

        for category_data in rating_categories:
            slug = slugify(category_data['name'])
            category, created = RatingCategory.objects.update_or_create(
                slug=slug,
                defaults={'name': category_data['name'], 'description': category_data['description']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created rating category: {category.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Rating category already exists: {category.name}'))

