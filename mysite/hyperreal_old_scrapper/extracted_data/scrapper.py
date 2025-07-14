import requests
from bs4 import BeautifulSoup
import os
import json
import time
from urllib.parse import urljoin, urlparse, unquote

# --- Konfiguracja początkowa ---
BASE_URL_HELP = "https://hyperreal.info/help/"
ALPHABETICAL_LIST_URL_SEGMENT = "alfabetyczny_spis_wszystkich_placowek"
CATEGORIES_URL_SEGMENT = "kategorie-placowek"
GLOSSARY_URL_SEGMENT = "glossary/"

OUTPUT_HTML_DIR = "scraped_hyperreal_help_html"
OUTPUT_DATA_PLACÓWKI_FILE = "placowki_data.json"
OUTPUT_DATA_GLOSSARY_FILE = "glossary_data.json"

REQUEST_DELAY = 1  # W sekundach
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Zbiory do śledzenia odwiedzonych/przetworzonych URL-i
visited_page_urls = set()  # URL-e stron, które zostały odwiedzone i ich HTML zapisany
processed_content_urls = set()  # URL-e, z których treść została sparsowana na potrzeby danych (np. placówki, glossary)

# Listy do przechowywania zebranych danych
all_placowki_data = []
all_glossary_data = []

# --- Funkcje pomocnicze ---

def create_directory(path):
    """Tworzy katalog, jeśli nie istnieje."""
    os.makedirs(path, exist_ok=True)

def get_local_path_for_url(url, base_output_dir):
    """Generuje lokalną ścieżkę do zapisu pliku HTML na podstawie URL."""
    parsed_url = urlparse(url)
    path = parsed_url.path
    if path.startswith('/'):
        path = path[1:] # Usuń wiodący slash

    # Usuń segment 'help/' jeśli istnieje, aby struktura była zgodna z BASE_URL_HELP
    if path.startswith('help/'):
        path = path[len('help/'):]

    query = parsed_url.query
    if query:
        # Dodaj query jako część nazwy pliku, aby odróżnić różne parametry
        path = f"{path.rstrip('/')}_{query.replace('=', '_').replace('&', '__')}"

    # Dekoduj procentowe kodowanie, ale usuń znaki, które mogą powodować problemy w nazwach plików
    path = unquote(path).replace('?', '_').replace(':', '_').replace('*', '_').replace('|', '_').replace('<', '_').replace('>', '_').replace('"', '_')

    if not path or path.endswith('/'):
        filename = "index.html"
    else:
        # Sprawdź, czy ścieżka ma rozszerzenie pliku, jeśli nie, dodaj .html
        if '.' not in os.path.basename(path):
            filename = os.path.basename(path) + ".html"
            path = os.path.dirname(path)
        else:
            filename = os.path.basename(path)
            path = os.path.dirname(path)

    full_dir_path = os.path.join(base_output_dir, path)
    create_directory(full_dir_path)
    return os.path.join(full_dir_path, filename)

def save_html_content(url, content, base_path_for_html_output):
    """Zapisuje zawartość HTML do pliku lokalnego, zachowując strukturę URL."""
    if url in visited_page_urls:
        print(f"  [HTML] URL już zapisany, pomijam: {url}")
        return

    local_path = get_local_path_for_url(url, base_path_for_html_output)
    try:
        with open(local_path, "wb") as f:
            f.write(content)
        print(f"  [HTML] Zapisano: {url} -> {local_path}")
        visited_page_urls.add(url)
    except IOError as e:
        print(f"  [BŁĄD] Nie można zapisać pliku {local_path} dla URL {url}: {e}")

def get_page_content_or_frame_content(page_url, session, base_path_for_html_output, parent_page_url=None):
    """
    Pobiera zawartość strony, sprawdza ramki (iframe/frame) i zwraca parsowany obiekt BeautifulSoup
    oraz URL, z którego pochodzi finalna treść. Zapisuje również HTML.
    """
    if page_url in visited_page_urls and page_url not in processed_content_urls:
        print(f"  [SKIP] Strona główna URL już odwiedzona, ale treść nie została jeszcze przetworzona: {page_url}")
        # Jeśli strona została już odwiedzona i zapisana, ale nie przetworzona, to po prostu ją wczytaj
        local_path = get_local_path_for_url(page_url, base_path_for_html_output)
        try:
            with open(local_path, "rb") as f:
                content = f.read()
            soup = BeautifulSoup(content, 'html.parser')
            print(f"  [INFO] Wczytano HTML z pliku dla {page_url}")
            return soup, page_url
        except FileNotFoundError:
            print(f"  [BŁĄD] Plik lokalny nie znaleziony, mimo że URL był w visited_page_urls: {local_path}")
            # Kontynuuj próbę pobrania
    elif page_url in processed_content_urls:
        print(f"  [SKIP] Treść z URL już przetworzona: {page_url}")
        return None, None # Nie ma potrzeby ponownie przetwarzać
    elif parent_page_url and parent_page_url in visited_page_urls and page_url in visited_page_urls:
        print(f"  [SKIP] Strona nadrzędna i zawartość ramki już odwiedzone i zapisane. URL ramki: {page_url}")
        return None, None


    print(f"Pobieram: {page_url}")
    try:
        response = session.get(page_url, timeout=10)
        response.raise_for_status()  # Sprawdź błędy HTTP
        save_html_content(page_url, response.content, base_path_for_html_output)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Sprawdzanie ramek
        frame_src = None
        # Obsługa iframe
        iframe = soup.find('iframe', src=True)
        if iframe:
            frame_src = iframe['src']
            print(f"  Znaleziono iframe: {frame_src}")
        else:
            # Obsługa starszych ramek (frame w frameset)
            frame = soup.find('frame', src=True)
            if frame:
                frame_src = frame['src']
                print(f"  Znaleziono frame: {frame_src}")

        if frame_src:
            frame_url = urljoin(page_url, frame_src)
            print(f"  Pobieram zawartość ramki z: {frame_url}")
            # Zapisz zawartość ramki również
            frame_response = session.get(frame_url, timeout=10)
            frame_response.raise_for_status()
            save_html_content(frame_url, frame_response.content, base_path_for_html_output)
            # Dalsze parsowanie powinno odbywać się na zawartości ramki
            return BeautifulSoup(frame_response.content, 'html.parser'), frame_url
        else:
            return soup, page_url

    except requests.exceptions.RequestException as e:
        print(f"  [BŁĄD] Błąd podczas pobierania {page_url}: {e}")
        return None, None
    finally:
        time.sleep(REQUEST_DELAY)

# --- Funkcje ekstrakcji danych ---

def extract_placowka_details(soup_object, content_source_url, parent_page_url):
    """
    Ekstrahuje szczegóły placówki z obiektu BeautifulSoup.
    Konieczne będzie dostosowanie selektorów.
    """
    if content_source_url in processed_content_urls:
        print(f"  [SKIP] Dane placówki z URL już przetworzone: {content_source_url}")
        return None

    data = {
        'nazwa': None,
        'adres': None,
        'telefon': None,
        'opis': None,
        'email': None,
        'www': None,
        'url_oryginalny_tresci': content_source_url,
        'url_strony_nadrzednej': parent_page_url
    }

    print(f"  Ekstrahuję dane placówki z: {content_source_url}")

    try:
        # Przykładowe selektory, wymagające dostosowania do faktycznej struktury HTML
        # Nazwa placówki (często H1/H2)
        name_tag = soup_object.find('h1', class_='page-header')
        if name_tag:
            data['nazwa'] = name_tag.get_text(strip=True)

        # Możliwe, że dane są w tabeli lub w divach
        # Poszukaj ogólnego kontenera dla danych placówki
        # content_div = soup_object.find('div', class_='content-area') # Przykładowy selektor

        # Przykładowe ekstrakcje:
        # Adres, telefon, email, www mogą być w paragrafach, listach lub w opisach
        # BARDZO WAŻNE: Poniższe selektory są hipotetyczne i MUSZĄ BYĆ DOSTOSOWANE do faktycznej struktury HTML.
        # Np. szukaj po etykietach "Adres:", "Telefon:", "Email:", "WWW:"
        
        # Przykład dla opisu, zakładając, że jest w tagu <p> lub <div> po nazwie
        description_tag = soup_object.find('div', class_='description') # lub inny odpowiedni selektor
        if description_tag:
            data['opis'] = description_tag.get_text(separator='\n', strip=True)
        else: # Jeśli nie ma dedykowanego diva, szukaj w paragrafach po nazwie
             # To jest bardzo ogólne i może wymagać doprecyzowania.
            paragraphs = soup_object.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                if "Adres:" in text:
                    data['adres'] = text.replace("Adres:", "").strip()
                elif "Telefon:" in text:
                    data['telefon'] = text.replace("Telefon:", "").strip()
                elif "Email:" in text:
                    data['email'] = text.replace("Email:", "").strip()
                elif "WWW:" in text:
                    data['www'] = text.replace("WWW:", "").strip()
                # Możesz tu również zaimplementować bardziej zaawansowaną logikę bazującą na wzorcach RegEx.

        # Dodaj więcej logiki ekstrakcji tutaj, bazując na konkretnej strukturze HTML hyperreal.info/help
        # Może być konieczne iterowanie po elementach <p> lub <li> w określonym divie
        # lub użycie wyrażeń regularnych do wyłapania danych.

        if data['nazwa']: # Tylko dodaj, jeśli udało się znaleźć nazwę
            all_placowki_data.append(data)
            processed_content_urls.add(content_source_url)
            print(f"  [OK] Zeskrapowano placówkę: {data['nazwa']}")
            return data
        else:
            print(f"  [OSTRZEŻENIE] Nie znaleziono nazwy placówki dla {content_source_url}. Pomijam.")
            return None

    except Exception as e:
        print(f"  [BŁĄD] Błąd podczas ekstrakcji danych placówki z {content_source_url}: {e}")
        return None

def extract_glossary_term_details(soup_object, content_source_url):
    """
    Ekstrahuje szczegóły terminu słownika z obiektu BeautifulSoup.
    Konieczne będzie dostosowanie selektorów.
    """
    if content_source_url in processed_content_urls:
        print(f"  [SKIP] Dane słownika z URL już przetworzone: {content_source_url}")
        return None

    data = {
        'termin': None,
        'definicja': None,
        'url_oryginalny_tresci': content_source_url
    }

    print(f"  Ekstrahuję dane słownika z: {content_source_url}")

    try:
        # Przykładowe selektory, wymagające dostosowania do faktycznej struktury HTML
        # Termin (często H1/H2 lub strong)
        term_tag = soup_object.find('h1') # lub inny selektor
        if term_tag:
            data['termin'] = term_tag.get_text(strip=True)

        # Definicja (często w paragrafie lub divie pod terminem)
        definition_tag = soup_object.find('div', class_='definition-content') # lub inny selektor
        if definition_tag:
            data['definicja'] = definition_tag.get_text(separator='\n', strip=True)
        else:
            # Bardziej ogólne wyszukiwanie definicji po terminie
            # Np. szukaj najbliższego paragrafu lub grupy paragrafów po tagu z terminem
            if term_tag:
                next_sibling = term_tag.find_next_sibling()
                if next_sibling and next_sibling.name in ['p', 'div']:
                    data['definicja'] = next_sibling.get_text(separator='\n', strip=True)


        if data['termin'] and data['definicja']:
            all_glossary_data.append(data)
            processed_content_urls.add(content_source_url)
            print(f"  [OK] Zeskrapowano termin słownika: {data['termin']}")
            return data
        else:
            print(f"  [OSTRZEŻENIE] Nie znaleziono terminu lub definicji dla {content_source_url}. Pomijam.")
            return None

    except Exception as e:
        print(f"  [BŁĄD] Błąd podczas ekstrakcji danych słownika z {content_source_url}: {e}")
        return None

# --- Główne funkcje crawlujące ---

def crawl_alphabetical_list(session, base_url, html_output_path):
    """
    Główna funkcja do nawigacji po spisie alfabetycznym placówek i zbierania danych.
    """
    print("\n--- Rozpoczynam skrapowanie placówek ---")
    alphabetical_main_url = urljoin(base_url, ALPHABETICAL_LIST_URL_SEGMENT)
    
    # Pobierz główną stronę spisu alfabetycznego
    main_soup, main_content_url = get_page_content_or_frame_content(
        alphabetical_main_url, session, html_output_path
    )

    if not main_soup:
        print(f"Błąd: Nie można pobrać głównej strony spisu alfabetycznego: {alphabetical_main_url}")
        return

    # Znajdź linki do poszczególnych liter alfabetu lub paginacji
    # Znowu, selektory muszą być dostosowane!
    # Szukaj linków, które prowadzą do np. ?litera=A, ?litera=B, etc.
    # Lub linków w tabeli, które mają teksty liter.
    
    # Przykład: linki do liter mogą być w divie z klasą 'alphabet-nav'
    letter_links = main_soup.find_all('a', href=True) # Bardzo ogólne
    
    # Przykładowa logika: znajdź unikalne URL-e dla liter, które wyglądają jak '?litera=X'
    unique_letter_urls = set()
    for link in letter_links:
        href = link['href']
        if 'litera=' in href or 'start=' in href: # Często używane do paginacji lub list alfabetycznych
            full_url = urljoin(main_content_url, href)
            unique_letter_urls.add(full_url)
        # Lub jeśli link jest po prostu literą
        elif len(link.get_text(strip=True)) == 1 and link.get_text(strip=True).isalpha():
            full_url = urljoin(main_content_url, href)
            unique_letter_urls.add(full_url)

    # Dodaj główny URL listy alfabetycznej, jeśli nie ma linków do liter (np. lista jest od razu na głównej stronie)
    if not unique_letter_urls:
        unique_letter_urls.add(alphabetical_main_url)

    # Przetwarzaj każdą stronę z listą liter
    for letter_url in sorted(list(unique_letter_urls)): # Sortowanie dla przewidywalnej kolejności
        if letter_url in processed_content_urls:
            print(f"  [SKIP] Strona listy liter już przetworzona: {letter_url}")
            continue

        print(f"\n--- Przetwarzam listę dla URL: {letter_url} ---")
        letter_soup, letter_content_url = get_page_content_or_frame_content(
            letter_url, session, html_output_path, parent_page_url=alphabetical_main_url
        )

        if not letter_soup:
            continue

        # Znajdź linki do indywidualnych placówek
        # Zakładając, że linki są w tabeli, np. <td><a>...</a></td>
        # Należy dokładnie sprawdzić strukturę HTML.
        
        placowka_links = letter_soup.select('td a[href*="help/placowka/"]') # Poprawiony selektor dla linków do placówek
        
        # Paginacja na stronach list alfabetycznych
        # Przykładowe selektory dla paginacji:
        # next_page_link = letter_soup.find('a', string=['Następna', 'Next'])
        # page_numbers = letter_soup.find_all('a', class_='page-number')

        current_page_placowka_urls = set()
        for link in placowka_links:
            href = link['href']
            full_placowka_url = urljoin(letter_content_url, href)
            current_page_placowka_urls.add(full_placowka_url)
        
        for placowka_url in current_page_placowka_urls:
            if placowka_url in processed_content_urls:
                print(f"  [SKIP] Dane placówki już przetworzone: {placowka_url}")
                continue

            placowka_soup, placowka_content_url = get_page_content_or_frame_content(
                placowka_url, session, html_output_path, parent_page_url=letter_url
            )
            if placowka_soup:
                extract_placowka_details(placowka_soup, placowka_content_url, placowka_url)
            
        processed_content_urls.add(letter_url) # Oznacz stronę listy jako przetworzoną

        # Logika paginacji (jeśli istnieje)
        # Należy to zaimplementować, jeśli strony listy placówek są paginowane.
        # Wymaga identyfikacji linków "Następna" lub numerów stron.
        # Przykładowa bardzo prosta pętla paginacji:
        # while next_page_link:
        #     next_href = next_page_link['href']
        #     next_full_url = urljoin(letter_content_url, next_href)
        #     if next_full_url in visited_page_urls: # Unikaj pętli nieskończonych
        #         print("  [Paginacja] Osiągnięto już odwiedzoną stronę, przerywam paginację.")
        #         break
        #     print(f"  [Paginacja] Przechodzę do następnej strony: {next_full_url}")
        #     next_letter_soup, next_letter_content_url = get_page_content_or_frame_content(
        #         next_full_url, session, html_output_path, parent_page_url=letter_url
        #     )
        #     if next_letter_soup:
        #         # Zidentyfikuj i przetwórz linki do placówek na tej stronie
        #         new_placowka_links = next_letter_soup.select('td a[href*="help/placowki/"]')
        #         for link in new_placowka_links:
        #             href = link['href']
        #             full_placowka_url = urljoin(next_letter_content_url, href)
        #             if full_placowka_url not in processed_content_urls:
        #                 placowka_soup, placowka_content_url = get_page_content_or_frame_content(
        #                     full_placowka_url, session, html_output_path, parent_page_url=next_full_url
        #                 )
        #                 if placowka_soup:
        #                     extract_placowka_details(placowka_soup, placowka_content_url, full_placowka_url)
        #         
        #         processed_content_urls.add(next_full_url)
        #         next_page_link = next_letter_soup.find('a', string=['Następna', 'Next']) # Znajdź link na nowej stronie
        #     else:
        #         break # Jeśli nie udało się pobrać następnej strony, przerwij paginację

def crawl_categories_list(session, base_url, html_output_path):
    """
    Funkcja do skrapowania placówek po kategoriach (z podkategorii).
    """
    print("\n--- Rozpoczynam skrapowanie placówek po kategoriach ---")
    categories_main_url = urljoin(base_url, CATEGORIES_URL_SEGMENT)

    main_soup, main_content_url = get_page_content_or_frame_content(
        categories_main_url, session, html_output_path
    )

    if not main_soup:
        print(f"Błąd: Nie można pobrać głównej strony kategorii placówek: {categories_main_url}")
        return

    # Zbierz linki do podkategorii
    category_links = main_soup.select('div.views-field-name span.field-content a[href]')
    unique_category_urls = set()
    for link in category_links:
        href = link['href']
        full_url = urljoin(main_content_url, href)
        unique_category_urls.add(full_url)

    # Jeśli nie ma podkategorii, spróbuj zebrać placówki bezpośrednio
    if not unique_category_urls:
        unique_category_urls.add(categories_main_url)

    for category_url in sorted(list(unique_category_urls)):
        if category_url in processed_content_urls:
            print(f"  [SKIP] Strona kategorii już przetworzona: {category_url}")
            continue

        print(f"\n--- Przetwarzam podkategorię: {category_url} ---")
        category_soup, category_content_url = get_page_content_or_frame_content(
            category_url, session, html_output_path, parent_page_url=categories_main_url
        )
        if not category_soup:
            continue

        # Szukaj linków do placówek w podkategorii
        placowka_links = category_soup.select('article header h2 a[href*="help/placowka/"]')
        current_page_placowka_urls = set()
        for link in placowka_links:
            href = link['href']
            full_placowka_url = urljoin(category_content_url, href)
            current_page_placowka_urls.add(full_placowka_url)

        for placowka_url in current_page_placowka_urls:
            if placowka_url in processed_content_urls:
                print(f"  [SKIP] Dane placówki już przetworzone: {placowka_url}")
                continue
            placowka_soup, placowka_content_url = get_page_content_or_frame_content(
                placowka_url, session, html_output_path, parent_page_url=category_url
            )
            if placowka_soup:
                extract_placowka_details(placowka_soup, placowka_content_url, placowka_url)

        processed_content_urls.add(category_url)

def crawl_glossary(session, base_url, html_output_path):
    """
    Funkcja do skrapowania danych słowniczka.
    """
    print("\n--- Rozpoczynam skrapowanie słowniczka ---")
    glossary_main_url = urljoin(base_url, GLOSSARY_URL_SEGMENT)

    main_soup, main_content_url = get_page_content_or_frame_content(
        glossary_main_url, session, html_output_path
    )

    if not main_soup:
        print(f"Błąd: Nie można pobrać głównej strony słowniczka: {glossary_main_url}")
        return

    # Znajdź linki do poszczególnych terminów lub list terminów.
    # Wymaga dostosowania selektorów.
    # Przykładowo, linki do terminów mogą być w <dt> lub <li>
    term_links = main_soup.select('a[href*="glossary/"]') # Ogólny selektor dla linków w glossary
    
    unique_term_urls = set()
    for link in term_links:
        href = link['href']
        full_url = urljoin(main_content_url, href)
        # Dodaj tylko linki, które wydają się prowadzić do konkretnych terminów, a nie np. do głównej strony glossary
        if 'glossary/' in full_url and full_url != glossary_main_url: # Upewnij się, że to link do terminu
            unique_term_urls.add(full_url)

    for term_url in sorted(list(unique_term_urls)):
        if term_url in processed_content_urls:
            print(f"  [SKIP] Dane terminu słownika już przetworzone: {term_url}")
            continue

        term_soup, term_content_url = get_page_content_or_frame_content(
            term_url, session, html_output_path, parent_page_url=glossary_main_url
        )
        if term_soup:
            extract_glossary_term_details(term_soup, term_content_url)
    
    processed_content_urls.add(glossary_main_url) # Oznacz główną stronę glossary jako przetworzoną

# --- Główna sekcja uruchamiająca skrypt ---

if __name__ == "__main__":
    # Tworzenie katalogu wyjściowego dla HTML
    create_directory(OUTPUT_HTML_DIR)

    # Inicjalizacja sesji requests
    session = requests.Session()
    session.headers.update({'User-Agent': USER_AGENT})

    print(f"Rozpoczynam skrapowanie {BASE_URL_HELP}...")

    try:
        # Skrapowanie placówek alfabetycznie
        crawl_alphabetical_list(session, BASE_URL_HELP, OUTPUT_HTML_DIR)
        # Skrapowanie placówek po kategoriach
        crawl_categories_list(session, BASE_URL_HELP, OUTPUT_HTML_DIR)
        # Skrapowanie słowniczka
        crawl_glossary(session, BASE_URL_HELP, OUTPUT_HTML_DIR)

    except Exception as e:
        print(f"Wystąpił ogólny błąd podczas skrapowania: {e}")

    finally:
        # Zapis zebranych danych do plików JSON
        print(f"\n--- Zapisywanie danych ---")
        try:
            with open(OUTPUT_DATA_PLACÓWKI_FILE, 'w', encoding='utf-8') as f:
                json.dump(all_placowki_data, f, ensure_ascii=False, indent=4)
            print(f"Zapisano dane placówek do: {OUTPUT_DATA_PLACÓWKI_FILE}")
        except IOError as e:
            print(f"Błąd podczas zapisu danych placówek: {e}")

        try:
            with open(OUTPUT_DATA_GLOSSARY_FILE, 'w', encoding='utf-8') as f:
                json.dump(all_glossary_data, f, ensure_ascii=False, indent=4)
            print(f"Zapisano dane słownika do: {OUTPUT_DATA_GLOSSARY_FILE}")
        except IOError as e:
            print(f"Błąd podczas zapisu danych słownika: {e}")

        print("\n--- Skrypt zakończył działanie ---")