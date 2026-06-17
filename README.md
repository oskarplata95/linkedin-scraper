# LinkedIn Scraper

Scraper profili LinkedIn oparty na [Apify API](https://apify.com).

## Wymagania

- Python 3.10+
- Konto Apify (darmowy plan wystarczy do testów)

## Instalacja

```bash
pip install -r requirements.txt
cp .env.example .env
# Wpisz swój token w pliku .env
```

Token API znajdziesz na: https://console.apify.com/account/integrations

## Użycie

### Scraping profili osób

```bash
python scraper.py --type person --urls https://www.linkedin.com/in/williamhgates/
```

### Scraping profili firm

```bash
python scraper.py --type company --urls https://www.linkedin.com/company/microsoft/
```

### Posty użytkownika

```bash
python scraper.py --type posts --urls https://www.linkedin.com/in/williamhgates/
```

### Wyniki wyszukiwania

```bash
python scraper.py --type search --urls "https://www.linkedin.com/search/results/people/?keywords=software+engineer"
```

### Wiele URL-i z pliku + zapis do JSON

```bash
python scraper.py --type person --file urls.txt --output output/results.json
```

Plik `urls.txt` — jeden URL na linię.

## Opcje

| Opcja | Opis |
|-------|------|
| `--type` | Typ danych: `person`, `company`, `posts`, `search` |
| `--urls` | Jeden lub więcej URL-i (space-separated) |
| `--file` | Plik tekstowy z URL-ami (jeden na linię) |
| `--output` | Ścieżka do wyjściowego pliku JSON (domyślnie: stdout) |

## Struktura wyników

Wyniki są zwracane jako tablica JSON. Przykładowe pola dla profilu osoby:

```json
{
  "fullName": "Bill Gates",
  "headline": "Co-chair, Bill & Melinda Gates Foundation",
  "location": "Seattle, Washington",
  "connections": 500,
  "about": "...",
  "experience": [...],
  "education": [...],
  "skills": [...]
}
```

## Używane aktory Apify

| Typ | Aktor Apify |
|-----|------------|
| `person` | LinkedIn Profile Scraper |
| `company` | LinkedIn Company Scraper |
| `posts` | LinkedIn Post Scraper |
| `search` | LinkedIn Search Scraper |
