# Raportare Șantiere Sector 1

Platformă civică pentru raportarea anonimă a șantierelor care nu respectă regulamentele de construcție din Sectorul 1, București.

Dezvoltat de [Cartiere Pentru Oameni](https://cartierepentruoameni.ro) - ONG axat pe transparență și participare cetățenească în dezvoltarea urbană.

## Funcționalități

- **Raportare anonimă** - Cetățenii pot raporta șantiere suspecte fără a-și dezvălui identitatea
- **Hartă interactivă** - Vizualizare toate raportările pe hartă
- **Upload fotografii** - Până la 10 poze per raportare (EXIF stripped automat pentru confidențialitate)
- **Verificare autorizații** - Căutare în baza de date cu autorizații de construire (PS1 + PMB)
- **Panou validator** - Validatori de încredere verifică și procesează raportările
- **Panou admin** - Gestionare utilizatori, rapoarte și date autorizații

## Tech Stack

- **Backend**: Flask 3.1 + Python
- **Database**: Supabase (PostgreSQL)
- **Storage**: Supabase Storage (pentru fotografii)
- **Frontend**: AdminLTE 3.2, Leaflet.js, Bootstrap

## Instalare

### 1. Clonează repository-ul

```bash
git clone <repo-url>
cd raportare-santiere
```

### 2. Creează environment virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# sau
venv\Scripts\activate  # Windows
```

### 3. Instalează dependențele

```bash
pip install -r requirements.txt
```

### 4. Configurează variabilele de mediu

Copiază `.env.example` în `.env` și completează valorile:

```bash
cp .env.example .env
```

Variabile necesare:
- `SECRET_KEY` - Cheie secretă Flask
- `SUPABASE_URL` - URL-ul proiectului Supabase
- `SUPABASE_ANON_KEY` - Cheie publică Supabase
- `SUPABASE_SERVICE_KEY` - Cheie service role Supabase

### 5. Configurează Supabase

1. Creează un proiect nou pe [supabase.com](https://supabase.com)
2. Rulează scripturile SQL din `schema.sql` și `migrations/`
3. Creează bucket-ul `report-pictures` (privat)

### 6. Creează primul admin

```bash
python scripts/create_admin.py
```

### 7. Rulează aplicația

```bash
python app.py
```

Aplicația va fi disponibilă la `http://localhost:5000`

## Structura Proiectului

```
raportare-santiere/
├── app/
│   ├── __init__.py          # App factory
│   ├── config.py            # Configurare din .env
│   ├── db.py                # Clienți Supabase
│   ├── helpers.py           # Funcții utilitare
│   ├── routes/
│   │   ├── public.py        # Rute publice
│   │   ├── auth.py          # Autentificare
│   │   ├── admin.py         # Panou admin
│   │   ├── validator.py     # Panou validator
│   │   ├── permits.py       # Modul autorizații
│   │   └── api.py           # Endpoint-uri API
│   └── scrapers/
│       ├── pmb.py           # Scraper PMB (urbanism.pmb.ro)
│       └── ps1.py           # Scraper PS1 (primariasector1.ro)
├── templates/               # Template-uri Jinja2
├── static/                  # CSS, JS, imagini
├── scripts/                 # Scripturi utilitare
├── migrations/              # Migrări SQL
├── app.py                   # Entry point
└── requirements.txt
```

## Workflow Raportări

1. **Pending** - Raportare nouă, ascunsă publicului
2. **In Review** - Validator verifică raportarea
3. **Validated** - Raportare confirmată ca legitimă
4. **Rejected** - Raportare respinsă
5. **Resolved** - Problemă rezolvată

## Confidențialitate

- Nu se colectează IP-uri sau user agents
- Datele EXIF sunt șterse automat din fotografii
- Raportările pending nu afișează descrierea/pozele public
- Row-Level Security (RLS) pe toate tabelele

## Licență

MIT

## Contact

- Website: [cartierepentruoameni.ro](https://cartierepentruoameni.ro)
