"""
Tippsi - eine Textverarbeitung mit Python und PySide6 (Qt)
Uni-Projekt

Diese Datei startet die Anwendung und erstellt das Hauptfenster.
"""

# ── Imports ──────────────────────────────────────────────
import sys
import os  # für Dateinamen (z. B. "brief.html" aus dem vollständigen Pfad)
from pathlib import Path  # für Dateipfade, z. B. zu den Design-Dateien

from PySide6.QtCore import Qt  # Qt-Grundeinstellungen, z. B. Farbschema
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTextEdit,
    QFileDialog,   # Standard-Dialog zum Öffnen und Speichern von Dateien
    QMessageBox,   # Popup-Meldungen, z. B. bei Fehlern
)
# QAction = ein Menüeintrag, QKeySequence = Tastenkürzel wie Strg+S
# QActionGroup = Gruppe von Menüeinträgen, von denen nur einer aktiv sein kann
from PySide6.QtGui import QAction, QActionGroup, QKeySequence


# ── Konstanten ───────────────────────────────────────────
# Ordner mit den Design-Dateien. __file__ ist der Pfad dieser main.py,
# .parent ist der Ordner, in dem sie liegt.
THEMES_DIR = Path(__file__).parent / "themes"

# Verfügbare Designs: Name im Menü -> (QSS-Datei, passendes Qt-Farbschema)
THEMES = {
    "Hell": ("light.qss", Qt.ColorScheme.Light),
    "Dunkel": ("dark.qss", Qt.ColorScheme.Dark),
}

# Qt-Stil für die Grunddarstellung. "Fusion" sieht auf allen Systemen
# gleich aus und beachtet Stylesheets vollständig.
QT_STYLE = "Fusion"


# ── Hauptfenster ─────────────────────────────────────────
class TippsiWindow(QMainWindow):
    """Das Hauptfenster von Tippsi.

    Erbt von QMainWindow und ergänzt Textfeld, Menüs und Dateifunktionen.
    """

    def __init__(self):
        """Konstruktor: wird automatisch beim Erstellen des Fensters ausgeführt."""
        super().__init__()

        # Pfad der aktuell geöffneten Datei.
        # None bedeutet: Das Dokument wurde noch nie gespeichert.
        self.current_file = None

        # --- Fenster-Grundeinstellungen ---
        self.resize(900, 650)
        self.update_title()

        # --- Textfeld ---
        # self.editor, damit andere Methoden (z. B. Speichern) darauf zugreifen können
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Text eingeben ...")
        self.setCentralWidget(self.editor)

        # --- Menüleiste ---
        self.create_file_menu()
        self.menuBar().addMenu("Bearbeiten")  # wird später ergänzt
        self.menuBar().addMenu("Format")      # wird später ergänzt
        self.create_view_menu()

        # --- Design ---
        # Beim Start das Design passend zur Systemeinstellung wählen
        self.apply_theme(self.system_theme())

    # ── Design ───────────────────────────────────────────
    def system_theme(self):
        """Gibt 'Dunkel' zurück, wenn das Betriebssystem im Dark Mode ist, sonst 'Hell'."""
        if QApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark:
            return "Dunkel"
        return "Hell"

    def apply_theme(self, name):
        """Wechselt das Design der Anwendung.

        name ist ein Schlüssel aus THEMES, z. B. "Hell" oder "Dunkel".
        """
        file_name, color_scheme = THEMES[name]

        # Qt-Farbschema anpassen, damit auch Standardfarben (z. B. Scrollleisten) passen
        QApplication.styleHints().setColorScheme(color_scheme)

        # Unser eigenes Design aus der QSS-Datei laden
        self.setStyleSheet((THEMES_DIR / file_name).read_text(encoding="utf-8"))

        # Häkchen im Menü beim richtigen Eintrag setzen
        self.theme_actions[name].setChecked(True)

    # ── Menüs ────────────────────────────────────────────
    def create_file_menu(self):
        """Erstellt das Datei-Menü mit Neu, Öffnen, Speichern und Beenden."""
        file_menu = self.menuBar().addMenu("Datei")

        # Jeder Menüeintrag ist eine QAction.
        # triggered.connect(...) verbindet den Klick mit einer Methode (Signal & Slot).
        new_action = QAction("Neu", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("Öffnen ...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Speichern", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Speichern unter ...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        quit_action = QAction("Beenden", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)  # close() stellt Qt bereit
        file_menu.addAction(quit_action)

    def create_view_menu(self):
        """Erstellt das Ansicht-Menü mit der Auswahl Hell/Dunkel."""
        view_menu = self.menuBar().addMenu("Ansicht")
        design_menu = view_menu.addMenu("Design")  # Untermenü

        # In einer QActionGroup kann immer nur ein Eintrag ausgewählt sein
        theme_group = QActionGroup(self)

        # Die Menüeinträge merken wir uns, um später das Häkchen setzen zu können
        self.theme_actions = {}

        # Für jedes Design in THEMES einen Menüeintrag erstellen
        for name in THEMES:
            action = QAction(name, self)
            action.setCheckable(True)  # Eintrag kann ein Häkchen bekommen
            # lambda = kleine Funktion ohne Namen. n=name merkt sich den
            # aktuellen Namen, sonst würden alle Einträge das letzte Design setzen.
            action.triggered.connect(lambda checked, n=name: self.apply_theme(n))
            theme_group.addAction(action)
            design_menu.addAction(action)
            self.theme_actions[name] = action

    # ── Dateifunktionen ──────────────────────────────────
    def new_file(self):
        """Leert das Textfeld und beginnt ein neues, unbenanntes Dokument."""
        self.editor.clear()
        self.current_file = None
        self.update_title()

    def open_file(self):
        """Öffnet eine vom Benutzer gewählte Datei und zeigt sie im Textfeld an."""
        # Rückgabe: (Pfad, gewählter Filter). Der Filter wird nicht benötigt -> _
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Datei öffnen",
            "",
            "Tippsi-Dokumente (*.html);;Textdateien (*.txt);;Alle Dateien (*)",
        )

        # Leerer Pfad = Benutzer hat abgebrochen
        if not path:
            return

        # try/except verhindert einen Absturz, falls die Datei nicht lesbar ist
        try:
            # UTF-8, damit Umlaute und Sonderzeichen korrekt gelesen werden
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError as error:
            QMessageBox.warning(self, "Fehler", f"Die Datei konnte nicht geöffnet werden:\n{error}")
            return

        # HTML inklusive Formatierung laden, andere Dateien als reinen Text
        if path.lower().endswith(".html"):
            self.editor.setHtml(content)
        else:
            self.editor.setPlainText(content)

        self.current_file = path
        self.update_title()

    def save_file(self):
        """Speichert in die aktuelle Datei oder ruft 'Speichern unter' auf."""
        if self.current_file is None:
            self.save_file_as()
        else:
            self.write_to_file(self.current_file)

    def save_file_as(self):
        """Fragt nach einem Speicherort und speichert das Dokument dort."""
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Speichern unter",
            "Unbenannt.html",
            "Tippsi-Dokumente (*.html);;Textdateien (*.txt)",
        )
        if not path:
            return

        # Ohne Dateiendung wird standardmäßig .html verwendet
        if not path.lower().endswith((".html", ".txt")):
            path += ".html"

        self.write_to_file(path)

    def write_to_file(self, path):
        """Schreibt den Inhalt des Textfelds in die angegebene Datei."""
        # .html speichert mit Formatierung, .txt nur den reinen Text
        if path.lower().endswith(".html"):
            content = self.editor.toHtml()
        else:
            content = self.editor.toPlainText()

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        except OSError as error:
            QMessageBox.warning(self, "Fehler", f"Die Datei konnte nicht gespeichert werden:\n{error}")
            return

        self.current_file = path
        self.update_title()
        # Hinweis in der Statusleiste, verschwindet nach 3 Sekunden
        self.statusBar().showMessage("Gespeichert", 3000)

    def update_title(self):
        """Zeigt den Namen der aktuellen Datei in der Titelleiste an."""
        if self.current_file:
            name = os.path.basename(self.current_file)
        else:
            name = "Unbenannt"
        self.setWindowTitle(f"{name} - Tippsi")


# ── Programmstart ────────────────────────────────────────
# Wird nur ausgeführt, wenn die Datei direkt gestartet wird (python main.py)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Einheitlichen Qt-Stil setzen, bevor Fenster erstellt werden
    app.setStyle(QT_STYLE)
    window = TippsiWindow()
    window.show()
    sys.exit(app.exec())