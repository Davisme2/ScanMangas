import random
import os
import time
import tkinter as tk
from tkinter import filedialog
from tqdm import tqdm


class UI:
    def __init__(self, db_manager, scraper):
        self.db = db_manager
        self.scraper = scraper
        self.header_ascii = r"""
          _____                  __  __                                  
         / ____|                |  \/  |                                 
        | (___   ___ __ _ _ __  | \  / | __ _ _ __   __ _  __ _  ___ _ __ 
         \___ \ / __/ _` | '_ \ | |\/| |/ _` | '_ \ / _` |/ _` |/ _ \ '__|
         ____) | (_| (_| | | | || |  | | (_| | | | | (_| | (_| |  __/ |   
        |_____/ \___\__,_|_| |_||_|  |_|\__,_|_| |_|\__,_|\__, |\___|_|   
                                                            __/ |          
                                                           |___/  v1.0 
        """
        self.current_manga = None

    def clear_console(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_header(self):
        self.clear_console()
        print(self.header_ascii)
        print("BIENVENUE\n")

    # MENU PRINCIPAL
    def main_loop(self):
        while True:
            self.display_header()
            choice = self.show_menu({
                '1': 'Consulter les mangas',
                '2': 'Mettre à jour la bibliothèque',
                '3': 'Quitter'
            })

            if choice == '1':
                self.show_mangas_list()
            elif choice == '2':
                self.update_library()
            elif choice == '3':
                break

    def show_menu(self, options):
        for key, value in options.items():
            print(f"{key}. {value}")
        return input("\n> ").strip()

    # GESTION MANGA
    def show_mangas_list(self):
        mangas = self.db.conn.execute('SELECT id, title FROM Manga ORDER BY title').fetchall()

        while True:
            self.display_header()
            print("=== LISTE DES MANGAS ===\n")

            for idx, (manga_id, title) in enumerate(mangas, 1):
                print(f"{idx}. {title}")

            choice = input("\nChoix (numéro/R: retour): ").strip().upper()

            if choice == 'R':
                return
            elif choice.isdigit():
                selected = int(choice) - 1
                if 0 <= selected < len(mangas):
                    self.current_manga = mangas[selected]
                    self.show_manga_details()
                else:
                    self.show_error("Numéro invalide !")
            else:
                self.show_error("Entrée invalide !")

    def show_manga_details(self):
        manga_id, title = self.current_manga
        details = self.db.conn.execute('''
            SELECT synopsis FROM Manga WHERE id = ?
        ''', (manga_id,)).fetchone()

        categories = self.db.conn.execute('''
            SELECT C.nom FROM Categorie C
            JOIN Manga_Categorie MC ON C.id = MC.categorie_id
            WHERE MC.manga_id = ?
        ''', (manga_id,)).fetchall()

        while True:
            self.display_header()
            print(f"=== {title.upper()} ===\n")
            print(f"Catégories: {', '.join([c[0] for c in categories])}")
            print(f"\nSynopsis:\n{details[0]}\n")

            choice = input("1. Voir les chapitres\n2. Retour\n> ").strip()

            if choice == '1':
                self.show_chapters_list()
            elif choice == '2':
                return
            else:
                self.show_error("Option invalide !")

    # GESTION CHAPITRES
    def show_chapters_list(self):
        chapters = self.db.conn.execute('''
            SELECT numero, date_publication, url 
            FROM Chapitre 
            WHERE manga_id = ?
            ORDER BY numero DESC
        ''', (self.current_manga[0],)).fetchall()

        current_page = 0
        chapters_per_page = 15
        total_pages = (len(chapters) // chapters_per_page) + 1

        while True:
            self.display_header()
            print(f"=== {self.current_manga[1].upper()} - CHAPITRES ===\n")

            # Afficher les chapitres avec index global
            start_idx = current_page * chapters_per_page
            displayed_chapters = chapters[start_idx:start_idx + chapters_per_page]

            for i, chap in enumerate(displayed_chapters, 1):
                global_index = start_idx + i
                print(f"{global_index}. Chapitre {chap[0]} - {chap[1]}")

            # Gestion de la sélection
            choice = input("\nChoix (numéro/plage/R/P/S): ").strip().upper()

            if choice == 'R':
                return
            elif choice == 'P' and current_page > 0:
                current_page -= 1
            elif choice == 'S' and current_page < total_pages - 1:
                current_page += 1
            else:
                try:
                    # Sélection par index global
                    if '-' in choice:
                        start, end = map(int, choice.split('-'))
                        selected = chapters[start-1:end]
                    else:
                        selected = [chapters[int(choice)-1]]

                    self.handle_download(selected)
                    return

                except (ValueError, IndexError):
                    self.show_error("Sélection invalide !")
                    time.sleep(1)

    def parse_chapter_selection(self, input_str, chapters):
        try:
            if '-' in input_str:
                start, end = map(float, input_str.split('-'))
                return [chap for chap in chapters if start <= chap[0] <= end]
            else:
                num = float(input_str)
                return [chap for chap in chapters if chap[0] == num]
        except:
            self.show_error("Format invalide !")
            return None

    # TELECHARGEMENT
    def handle_download(self, chapters):
        self.display_header()
        print("=== SELECTION DU DOSSIER ===\n")

        # Sélection du dossier
        path = self.select_directory() if input("Choisir un dossier? (O/n) ").strip().upper() == 'O' \
            else os.path.expanduser("~/Desktop/ScanMangas")

        os.makedirs(path, exist_ok=True)

        # Barre de progression principale
        total_images = sum(len(self.scraper.get_chapter_images(chap[2])) for chap in chapters)

        with tqdm(
                total=total_images,
                desc="Progression globale",
                unit='img',
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"
        ) as main_bar:

            for chap in chapters:
                chap_num = chap[0]
                chap_path = os.path.join(path, f"Chapitre {chap_num}")
                os.makedirs(chap_path, exist_ok=True)

                # Téléchargement avec suivi hiérarchique
                success, images = self.scraper.download_images(
                    chapter_url=chap[2],
                    output_path=chap_path,
                    main_bar=main_bar
                )

                if success < len(images):
                    main_bar.write(
                        f"Avertissement: {len(images) - success} images manquantes dans le chapitre {chap_num}")

        print("\nTéléchargement terminé !")
        input("Appuyez sur Entrée pour continuer...")

    # FONCTIONS UTILITAIRES
    def select_directory(self):
        root = tk.Tk()
        root.withdraw()
        return filedialog.askdirectory()

    def show_error(self, message):
        print(f"\nERREUR: {message}")
        time.sleep(2)

    # MISE À JOUR BIBLIOTHEQUE
    def update_library(self):
        self.display_header()
        print("=== MISE À JOUR EN COURS ===\n")

        try:
            self.db.backup_db()
            page = 1

            with tqdm(desc="Scan des pages", unit="page") as pbar:
                while True:
                    mangas = self.scraper.get_manga_list(page)
                    if not mangas: break

                    for title, url in mangas:
                        details = self.scraper.get_manga_details(url)
                        if details:
                            synopsis, categories, chapters = details
                            manga_id = self.db.insert_manga(title, synopsis, url, categories)
                            self.db.update_chapters(manga_id, chapters)

                    page += 1
                    pbar.update(1)
                    time.sleep(random.uniform(2, 5))

            print("\nMise à jour terminée avec succès !")
        except Exception as e:
            print(f"\nERREUR CRITIQUE: {str(e)}")

        time.sleep(3)