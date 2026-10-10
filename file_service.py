"""
Dateizugriffe von Tippsi: Lesen, Schreiben und Dateiendungen.

Dieses Modul enthält bewusst keinen Qt-Code. Dadurch ist die Dateilogik
unabhängig von der Oberfläche und kann später mit Unit-Tests geprüft werden.
"""

from pathlib import Path

# Dateiendungen, die Tippsi speichern kann
SUPPORTED_EXTENSIONS = (".html", ".txt")

# Wird verwendet, wenn der Benutzer keine Endung angibt
DEFAULT_EXTENSION = ".html"


def is_html(path):
    """Prüft, ob der Pfad auf eine HTML-Datei zeigt (Groß-/Kleinschreibung egal)."""
    return Path(path).suffix.lower() == ".html"


def ensure_extension(path):
    """Hängt DEFAULT_EXTENSION an, falls der Pfad keine unterstützte Endung hat."""
    if Path(path).suffix.lower() in SUPPORTED_EXTENSIONS:
        return path
    return path + DEFAULT_EXTENSION


def read_file(path):
    """Liest eine Datei als UTF-8-Text und gibt den Inhalt zurück.

    Wirft OSError, wenn die Datei nicht gelesen werden kann.
    Die Fehlermeldung für den Benutzer zeigt das Hauptfenster an.
    """
    return Path(path).read_text(encoding="utf-8")


def read_lines(path):
    """Liest eine Textdatei und gibt alle nicht-leeren Zeilen als Liste zurück.

    Leerzeichen am Anfang und Ende jeder Zeile werden entfernt.
    Wirft OSError, wenn die Datei nicht gelesen werden kann.
    """
    lines = read_file(path).splitlines()
    return [line.strip() for line in lines if line.strip()]


def write_file(path, content):
    """Schreibt Text als UTF-8 in eine Datei.

    Wirft OSError, wenn die Datei nicht geschrieben werden kann.
    """
    Path(path).write_text(content, encoding="utf-8")