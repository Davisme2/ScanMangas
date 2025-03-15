import os

import requests
from bs4 import BeautifulSoup
import random
import time
from urllib.parse import urljoin
from tqdm import tqdm


class Scraper:
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X)',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0)'
    ]

    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.current_agent = random.choice(self.USER_AGENTS)

    def _get_headers(self):
        return {'User-Agent': self.current_agent}

    def fetch_page(self, url, max_retries=3):
        for _ in range(max_retries):
            try:
                response = self.session.get(url, headers=self._get_headers(), timeout=10)
                response.encoding = 'utf-8'
                try:
                    return BeautifulSoup(response.text, 'lxml')
                except Exception:
                    return BeautifulSoup(response.text, 'html.parser')
            except Exception as e:
                print(f"Erreur: {e}. Nouvelle tentative...")
                time.sleep(random.uniform(2, 5))
        return None

    # Dans la méthode get_manga_list()
    def get_manga_list(self, page=1):
        url = f"{self.base_url}/page/{page}/"
        soup = self.fetch_page(url)
        mangas = []

        for item in soup.select('div.listupd > div'):
            # Correction ici : utilisation de l'attribut "title" au lieu du texte
            title_elem = item.select_one('a[title]')

            if title_elem and title_elem.has_attr('title'):
                title = title_elem['title'].strip()
                url = urljoin(self.base_url, title_elem['href'])
                mangas.append((title, url))

        return mangas

    def get_manga_details(self, url):
        soup = self.fetch_page(url)
        if not soup:
            return None

        try:
            # Catégories
            categories = []
            category_elems = soup.select('div.info-desc.bixbox > div:nth-child(2) > span')
            for span in category_elems:
                categories.append(span.text.strip())

            # Synopsis
            synopsis_elem = soup.select_one('div.info-desc.bixbox > div:nth-child(3) > div > p:nth-child(1)')
            synopsis = synopsis_elem.text.strip() if synopsis_elem else "Synopsis non disponible"

            # Chapitres
            chapters = []
            for li in soup.select('#chapterlist ul li'):
                chap_num_elem = li.select_one('span.chapternum')
                date_elem = li.select_one('span.chapterdate')

                if chap_num_elem and date_elem:
                    chap_num = chap_num_elem.text.strip().split()[-1]
                    date = date_elem.text.strip()
                    chap_url = urljoin(self.base_url, li.select_one('a')['href'])
                    chapters.append((chap_num, date, chap_url))

            return synopsis, categories, chapters

        except Exception as e:
            print(f"Erreur lors du parsing: {str(e)}")
            return None

    def download_images(self, chapter_url, output_path, main_bar=None):
        soup = self.fetch_page(chapter_url)
        if not soup:
            return 0

        images = [
            img.get('src') or img.get('data-src')
            for img in soup.select('#readerarea img')
            if img.get('src') or img.get('data-src')
        ]

        success = 0
        chap_bar = tqdm(
            images,
            desc=f"Chapitre {os.path.basename(chapter_url)}",
            leave=False,
            unit='img'
        )

        for idx, img_url in enumerate(chap_bar, 1):
            try:
                response = self.session.get(img_url, timeout=15)
                if response.status_code == 200:
                    with open(f"{output_path}/page_{idx:03d}.jpg", 'wb') as f:
                        f.write(response.content)
                    success += 1

                if main_bar:
                    main_bar.update(1)

                time.sleep(random.uniform(1, 3))

            except Exception as e:
                chap_bar.write(f"Erreur: {str(e)}")

        chap_bar.close()
        return success, images

    def get_chapter_images(self, chapter_url):
        """Récupère uniquement les URLs des images sans télécharger"""
        soup = self.fetch_page(chapter_url)
        if not soup:
            return []

        return [
            img.get('src') or img.get('data-src')
            for img in soup.select('#readerarea img')
            if img.get('src') or img.get('data-src')
        ]