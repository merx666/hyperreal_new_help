from django.core.management.base import BaseCommand
from help_section.models import Facility
from geopy.geocoders import MapBox
import time

MAPBOX_TOKEN = "pk.eyJ1IjoibWVyeDY2NiIsImEiOiJjbWQzNTU3NzUwMHc5MmlzY3c1amMyM210In0.QlqywCju2F2M_m5NDtvAVQ"

class Command(BaseCommand):
    help = 'Geokoduje adresy placówek używając Mapbox Geocoding API'

    def handle(self, *args, **options):
        geolocator = MapBox(api_key=MAPBOX_TOKEN, timeout=10)
        facilities = Facility.objects.filter(latitude__isnull=True, longitude__isnull=True)
        self.stdout.write(f"Znaleziono {facilities.count()} placówek do geokodowania (Mapbox)")
        for i, facility in enumerate(facilities, 1):
            address_parts = []
            if facility.address_street:
                address_parts.append(facility.address_street)
            if facility.address_city:
                address_parts.append(facility.address_city)
            if facility.voivodeship:
                address_parts.append(facility.voivodeship)
            address_parts.append("Poland")
            if len(address_parts) < 2:
                self.stdout.write(f"[{i}] Pominięto (za mało danych): {facility.name}")
                continue
            address = ", ".join(address_parts)
            try:
                location = geolocator.geocode(address)
                if location:
                    facility.latitude = location.latitude
                    facility.longitude = location.longitude
                    facility.save()
                    self.stdout.write(f"[{i}] ✓ {facility.name}: {facility.latitude}, {facility.longitude}")
                else:
                    self.stdout.write(f"[{i}] ✗ Nie znaleziono: {facility.name} ({address})")
            except Exception as e:
                self.stdout.write(f"[{i}] ✗ Błąd: {facility.name} ({address}) - {e}")
            time.sleep(0.2)  # Mapbox pozwala na szybkie zapytania, ale nie przesadzajmy
        self.stdout.write("Geokodowanie Mapbox zakończone!") 