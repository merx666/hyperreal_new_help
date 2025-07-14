from django.core.management.base import BaseCommand
from help_section.models import Facility
import requests
import time
from django.conf import settings

class Command(BaseCommand):
    help = 'Geokoduje adresy placówek używając OpenStreetMap Nominatim API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Przeprowadź geokodowanie nawet dla placówek, które już mają współrzędne',
        )

    def handle(self, *args, **options):
        facilities = Facility.objects.all()
        
        if not options['force']:
            facilities = facilities.filter(latitude__isnull=True, longitude__isnull=True)
        
        self.stdout.write(f"Znaleziono {facilities.count()} placówek do geokodowania")
        
        for i, facility in enumerate(facilities, 1):
            self.stdout.write(f"[{i}/{facilities.count()}] Geokodowanie: {facility.name}")
            
            # Przygotuj adres do geokodowania
            address_parts = []
            if facility.address_street:
                address_parts.append(facility.address_street)
            if facility.address_city:
                address_parts.append(facility.address_city)
            if facility.voivodeship:
                address_parts.append(facility.voivodeship)
            address_parts.append("Poland")
            
            if len(address_parts) < 2:
                self.stdout.write(self.style.WARNING(f"  Pominięto - za mało danych adresowych"))
                continue
            
            address = ", ".join(address_parts)
            
            try:
                # Wywołaj Nominatim API
                url = "https://nominatim.openstreetmap.org/search"
                params = {
                    'q': address,
                    'format': 'json',
                    'limit': 1,
                    'countrycodes': 'pl'
                }
                
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                if data:
                    result = data[0]
                    facility.latitude = float(result['lat'])
                    facility.longitude = float(result['lon'])
                    facility.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(f"  ✓ Zaktualizowano: {facility.latitude}, {facility.longitude}")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"  ✗ Nie znaleziono współrzędnych dla: {address}")
                    )
                
                # Rate limiting - Nominatim wymaga maksymalnie 1 zapytania na sekundę
                time.sleep(1)
                
            except requests.RequestException as e:
                self.stdout.write(
                    self.style.ERROR(f"  ✗ Błąd API: {e}")
                )
                time.sleep(2)  # Dłuższe oczekiwanie w przypadku błędu
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  ✗ Błąd: {e}")
                )
        
        self.stdout.write(self.style.SUCCESS("Geokodowanie zakończone!")) 