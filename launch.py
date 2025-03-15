# core/__init__.py
from core.scraper import Scraper
from core.db_manager import DBManager
from core.ui import UI


def main():
    scraper = Scraper("https://rimuscans.fr")
    db = DBManager()
    ui = UI(db, scraper)
    ui.main_loop()


if __name__ == "__main__":
    main()