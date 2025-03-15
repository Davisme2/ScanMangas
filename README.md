# ScanMangas 🐍📚

Un script Python pour télécharger et organiser des scans de mangas depuis [rimuscans.fr](https://rimuscans.fr)

## Fonctionnalités
- Interface console interactive
- Base de données locale SQLite
- Téléchargement batch des chapitres
- Gestion des catégories
- Système de cache intelligent

## Installation
1. Clonez le dépôt :
```bash
git clone https://github.com/votre-utilisateur/ScanMangas.git
cd ScanMangas
```

2. Installez les dépendances :
```bash
./install.bat  # Windows
# ou
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # Linux/Mac
```

## Utilisation
1. Lancez le script :
```bash
./launch.bat  # Windows
# ou
python launch.py  # Linux/Mac
```

2. Navigation dans le menu :
```
1. Consulter les mangas    → Sélection par numéro/plage
2. Mettre à jour la DB     ← Actualise les nouveautés
3. Quitter
```

## Configuration
Modifiez `config/settings.ini` :
```ini
[paths]
default_download = ~/Documents/ScanMangas

[scraping]
request_delay = 2-5  # Délai entre requêtes
max_retries = 3       # Tentatives de connexion
```

## Dépendances
- Python 3.10+
- Bibliothèques : `requests`, `beautifulsoup4`, `tqdm`, `lxml`

## Dépannage
Erreur commune | Solution
--------------|---------
`Missing lxml` | Réexécutez `install.bat`
`DB locked`    | Supprimez `data/scanmangas.db`
`SSL Error`    | Mettez à jour OpenSSL

## Licence
MIT License - Voir [LICENSE](LICENSE)

## Contribution
Les PR sont les bienvenues ! Ouvrez une issue pour discuter des améliorations.