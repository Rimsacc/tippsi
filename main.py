"""
Tippsi - eine Textverarbeitung mit Python und PySide6 (Qt)
Uni-Projekt

Diese Datei startet die Anwendung und erstellt das Hauptfenster.
"""

# ── Imports ──────────────────────────────────────────────
import sys
import os  # für Dateinamen (z. B. "brief.html" aus dem vollständigen Pfad)

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTextEdit,
    QFileDialog,   # Standard-Dialog zum Öffnen und Speichern von Dateien
    QMessageBox,   # Popup-Meldungen, z. B. bei Fehlern
)
# QAction = ein Menüeintrag, QKeySequence = Tastenkürzel wie Strg+S
from PySide6.QtGui import QAction, QKeySequence


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

        # --- Design ---
        self.apply_style()

    # ── Design ───────────────────────────────────────────
    def apply_style(self):
        """Setzt das Farbschema der Anwendung per Qt Style Sheet (QSS)."""
        self.setStyleSheet("""
            QMainWindow { background-color: #FFE4EC; }

            QMenuBar {
                background-color: #FFB6C8;
                color: white;
                font-weight: bold;
            }
            QMenuBar::item:selected { background-color: #FF8FAB; }

            QMenu {
                background-color: #FFFAFC;
                border: 1px solid #FFB6C8;
            }
            QMenu::item:selected { background-color: #FFD1DC; color: #4A4A4A; }

            QTextEdit {
                background-color: #FFFAFC;
                color: #4A4A4A;
                border: 2px solid #FFB6C8;
                border-radius: 12px;
                margin: 16px;
                padding: 12px;
                font-size: 14px;
            }

            QStatusBar { color: #FF8FAB; font-weight: bold; }
        """)

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
    window = TippsiWindow()
    window.show()
    sys.exit(app.exec())