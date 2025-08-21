# HyperReal Help 🏥

Nowoczesna platforma internetowa do wyszukiwania i oceniania placówek medycznych w Polsce. Projekt został stworzony z myślą o ułatwieniu pacjentom znalezienia odpowiedniej opieki medycznej.

## 🌟 Funkcjonalności

### 🔍 Zaawansowane wyszukiwanie
- Wyszukiwanie placówek według nazwy, lokalizacji i specjalizacji
- Filtry zaawansowane (typ placówki, oceny, dostępność)
- Inteligentne sugestie wyszukiwania

### 🗺️ Interaktywna mapa
- Wizualizacja placówek na mapie
- Geolokalizacja użytkownika
- Wyświetlanie szczegółów placówek w popup'ach

### ⭐ System ocen i recenzji
- Ocenianie placówek w skali 1-5 gwiazdek
- Szczegółowe recenzje użytkowników
- Ranking najlepszych placówek
- Statystyki i średnie ocen

### 🔔 System powiadomień
- Powiadomienia o nowych placówkach
- Alerty o zmianach w ulubionych placówkach
- Personalizowane preferencje powiadomień

### ♿ Dostępność
- Pełna zgodność z WCAG 2.1
- Obsługa czytników ekranu
- Nawigacja klawiaturą
- Tryb ciemny (dark mode)
- Responsywny design

### 📱 Responsywność
- Optymalizacja dla urządzeń mobilnych
- Adaptacyjny interfejs użytkownika
- Touch-friendly kontrolki

## 🛠️ Technologie

### Backend
- **Django 5.0** - Framework webowy
- **Python 3.11+** - Język programowania
- **SQLite** - Baza danych (development)
- **Django REST Framework** - API

### Frontend
- **HTML5** - Struktura
- **CSS3** - Stylowanie z obsługą dark mode
- **JavaScript (ES6+)** - Interaktywność
- **Bootstrap 5** - Framework CSS
- **Font Awesome** - Ikony

### Narzędzia i biblioteki
- **Leaflet** - Interaktywne mapy
- **HTMX** - Dynamiczne aktualizacje
- **Django Sitemap** - SEO
- **Accessibility features** - ARIA, semantic HTML

## 🚀 Instalacja i uruchomienie

### Wymagania
- Python 3.11 lub nowszy
- pip (menedżer pakietów Python)
- Git

### Kroki instalacji

1. **Klonowanie repozytorium**
   ```bash
   git clone https://github.com/merx666/hyperreal_new_help.git
   cd hyperreal_new_help
   ```

2. **Tworzenie środowiska wirtualnego**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # lub
   venv\Scripts\activate     # Windows
   ```

3. **Instalacja zależności**
   ```bash
   cd mysite
   pip install -r requirements.txt
   ```

4. **Migracje bazy danych**
   ```bash
   python manage.py migrate
   ```

5. **Tworzenie superusera (opcjonalne)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Uruchomienie serwera deweloperskiego**
   ```bash
   python manage.py runserver
   ```

7. **Otwórz przeglądarkę**
   Przejdź do `http://localhost:8000/help/`

## 📁 Struktura projektu

```
hyperreal_new_help/
├── mysite/                     # Główny katalog Django
│   ├── help_section/          # Główna aplikacja
│   │   ├── models.py          # Modele danych
│   │   ├── views.py           # Widoki
│   │   ├── urls.py            # Routing URL
│   │   ├── forms.py           # Formularze
│   │   ├── admin.py           # Panel administracyjny
│   │   ├── static/            # Pliki statyczne
│   │   │   ├── css/           # Style CSS
│   │   │   ├── js/            # Skrypty JavaScript
│   │   │   └── images/        # Obrazy
│   │   ├── templates/         # Szablony HTML
│   │   └── migrations/        # Migracje bazy danych
│   ├── mysite/                # Konfiguracja projektu
│   │   ├── settings.py        # Ustawienia Django
│   │   ├── urls.py            # Główny routing
│   │   └── wsgi.py            # WSGI config
│   ├── manage.py              # Narzędzie zarządzania Django
│   └── requirements.txt       # Zależności Python
├── README.md                  # Ten plik
└── .gitignore                # Pliki ignorowane przez Git
```

## 🎨 Funkcjonalności UI/UX

- **Dark Mode**: Automatyczne przełączanie między trybem jasnym i ciemnym
- **Animacje**: Płynne przejścia i efekty hover
- **Responsywność**: Optymalizacja dla wszystkich rozmiarów ekranów
- **Accessibility**: Pełna obsługa czytników ekranu i nawigacji klawiaturą
- **Performance**: Optymalizowane ładowanie i renderowanie

## 🔧 Konfiguracja

### Zmienne środowiskowe
Utwórz plik `.env` w katalogu `mysite/` z następującymi zmiennymi:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Konfiguracja bazy danych
Dla produkcji zaleca się użycie PostgreSQL. Zaktualizuj `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'hyperreal_help',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 🧪 Testowanie

```bash
# Uruchomienie testów
python manage.py test

# Testowanie z pokryciem kodu
coverage run --source='.' manage.py test
coverage report
```

## 📈 SEO i Performance

- **Sitemap XML**: Automatycznie generowana mapa strony
- **Robots.txt**: Konfiguracja dla robotów wyszukiwarek
- **Meta tags**: Optymalizowane dla wyszukiwarek
- **Lazy loading**: Obrazy ładowane na żądanie
- **Minifikacja**: Zoptymalizowane pliki CSS i JS

## 🤝 Współpraca

1. Fork repozytorium
2. Utwórz branch dla nowej funkcjonalności (`git checkout -b feature/AmazingFeature`)
3. Commit zmian (`git commit -m 'Add some AmazingFeature'`)
4. Push do branch (`git push origin feature/AmazingFeature`)
5. Otwórz Pull Request

## 📝 Licencja

Ten projekt jest dostępny na licencji MIT. Zobacz plik `LICENSE` dla szczegółów.

## 👥 Autorzy

- **merx666** - *Główny deweloper* - [GitHub](https://github.com/merx666)

## 🙏 Podziękowania

- Django community za doskonały framework
- Bootstrap team za responsywny framework CSS
- Leaflet za bibliotekę map
- Wszystkim kontrybutorów i testerom

## 📞 Kontakt

Jeśli masz pytania lub sugestie, skontaktuj się poprzez:
- GitHub Issues: [Issues](https://github.com/merx666/hyperreal_new_help/issues)
- Email: [Kontakt przez GitHub](https://github.com/merx666)

---

**HyperReal Help** - Znajdź odpowiednią opiekę medyczną 🏥✨

