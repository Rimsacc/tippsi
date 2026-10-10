"""
Tippsi - eine Textverarbeitung mit Python und PySide6 (Qt)
Uni-Projekt

Diese Datei startet die Anwendung und erstellt das Hauptfenster.
"""

# ── Imports ──────────────────────────────────────────────
import sys
import random  # für die zufällige Auswahl des Platzhaltertexts
from pathlib import Path  # für Dateipfade, z. B. zu den Design-Dateien

from PySide6.QtCore import Qt  # Qt-Grundeinstellungen, z. B. Farbschema
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTextEdit,
    QFileDialog,   # Standard-Dialog zum Öffnen und Speichern von Dateien
    QMessageBox,   # Popup-Meldungen, z. B. bei Fehlern oder Rückfragen
)
# QAction = ein Menüeintrag, QKeySequence = Tastenkürzel wie Strg+S
# QActionGroup = Gruppe von Menüeinträgen, von denen nur einer aktiv sein kann
from PySide6.QtGui import QAction, QActionGroup, QKeySequence

# Eigene Module
import file_service                      # Lesen und Schreiben von Dateien
from format_toolbar import FormatToolbar  # Toolbar für fett, kursiv usw.


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

# Filter für die Datei-Dialoge (Text im Dialog und erlaubte Endungen)
FILE_FILTER_OPEN = "Tippsi-Dokumente (*.html);;Textdateien (*.txt);;Alle Dateien (*)"
FILE_FILTER_SAVE = "Tippsi-Dokumente (*.html);;Textdateien (*.txt)"

# Standard-Schriftgröße im Textfeld (in Punkt, wie in Word)
DEFAULT_FONT_SIZE = 12

# Datei mit den Platzhaltertexten (eine Zeile = ein Text).
# Die Texte stehen bewusst nicht im Code, sondern in einer eigenen Datei.
PLACEHOLDERS_PATH = Path(__file__).parent / "texts" / "placeholders.txt"

# Wird verwendet, falls die Datei fehlt oder leer ist
DEFAULT_PLACEHOLDER = "Text eingeben ..."


# ── Hauptfenster ─────────────────────────────────────────
class TippsiWindow(QMainWindow):
    """Das Hauptfenster von Tippsi.

    Zuständig für Anzeige und Bedienung. Das Lesen und Schreiben
    von Dateien übernimmt das Modul file_service, die Formatierung
    die Klasse FormatToolbar.
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
        self.placeholders = self.load_placeholders()
        self.set_random_placeholder()
        self.set_default_font()
        self.setCentralWidget(self.editor)

        # Observer: Sobald sich der Text ändert (oder gespeichert wird),
        # meldet das Dokument das, und Qt zeigt ein * im Fenstertitel an.
        self.editor.document().modificationChanged.connect(self.setWindowModified)

        # --- Toolbar ---
        # Die Toolbar bekommt das Textfeld, damit sie es formatieren kann
        self.format_toolbar = FormatToolbar(self.editor, self)
        self.addToolBar(self.format_toolbar)

        # --- Menüleiste ---
        self.create_file_menu()
        self.create_edit_menu()
        self.create_format_menu()
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
    def make_action(self, text, shortcut, slot):
        """Hilfsmethode: erstellt einen Menüeintrag mit Tastenkürzel.

        slot ist die Methode, die beim Klick ausgeführt wird (Signal & Slot).
        """
        action = QAction(text, self)
        action.setShortcut(shortcut)
        action.triggered.connect(slot)
        return action

    def create_file_menu(self):
        """Erstellt das Datei-Menü mit Neu, Öffnen, Speichern und Beenden."""
        file_menu = self.menuBar().addMenu("Datei")
        keys = QKeySequence.StandardKey

        file_menu.addAction(self.make_action("Neu", keys.New, self.new_file))
        file_menu.addAction(self.make_action("Öffnen ...", keys.Open, self.open_file))
        file_menu.addAction(self.make_action("Speichern", keys.Save, self.save_file))
        file_menu.addAction(self.make_action("Speichern unter ...", keys.SaveAs, self.save_file_as))
        file_menu.addSeparator()
        file_menu.addAction(self.make_action("Beenden", keys.Quit, self.close))

    def create_edit_menu(self):
        """Erstellt das Bearbeiten-Menü (Rückgängig, Kopieren, Einfügen usw.).

        Die eigentlichen Funktionen bringt QTextEdit schon mit.
        """
        edit_menu = self.menuBar().addMenu("Bearbeiten")
        keys = QKeySequence.StandardKey

        undo_action = self.make_action("Rückgängig", keys.Undo, self.editor.undo)
        redo_action = self.make_action("Wiederholen", keys.Redo, self.editor.redo)
        cut_action = self.make_action("Ausschneiden", keys.Cut, self.editor.cut)
        copy_action = self.make_action("Kopieren", keys.Copy, self.editor.copy)
        paste_action = self.make_action("Einfügen", keys.Paste, self.editor.paste)
        select_all_action = self.make_action("Alles auswählen", keys.SelectAll, self.editor.selectAll)

        # Am Anfang gibt es nichts rückgängig zu machen und nichts markiert
        for action in (undo_action, redo_action, cut_action, copy_action):
            action.setEnabled(False)

        # Observer: Das Textfeld meldet, wann diese Aktionen möglich sind,
        # und die Menüeinträge werden automatisch an- oder ausgegraut.
        self.editor.undoAvailable.connect(undo_action.setEnabled)
        self.editor.redoAvailable.connect(redo_action.setEnabled)
        self.editor.copyAvailable.connect(cut_action.setEnabled)
        self.editor.copyAvailable.connect(copy_action.setEnabled)

        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(cut_action)
        edit_menu.addAction(copy_action)
        edit_menu.addAction(paste_action)
        edit_menu.addSeparator()
        edit_menu.addAction(select_all_action)

    def create_format_menu(self):
        """Erstellt das Format-Menü.

        Verwendet dieselben Aktionen wie die Toolbar. Dadurch sind Menü
        und Toolbar immer gleich (Häkchen, Tastenkürzel) und nichts ist doppelt.
        """
        format_menu = self.menuBar().addMenu("Format")
        format_menu.addAction(self.format_toolbar.bold_action)
        format_menu.addAction(self.format_toolbar.italic_action)
        format_menu.addAction(self.format_toolbar.underline_action)

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
        # Vorher fragen, falls es ungespeicherte Änderungen gibt
        if not self.maybe_save():
            return

        self.editor.clear()
        self.set_random_placeholder()  # bei jedem neuen Dokument ein anderer Spruch
        self.set_current_file(None)

    def open_file(self):
        """Öffnet eine vom Benutzer gewählte Datei und zeigt sie im Textfeld an."""
        # Vorher fragen, falls es ungespeicherte Änderungen gibt
        if not self.maybe_save():
            return

        # Rückgabe: (Pfad, gewählter Filter). Der Filter wird nicht benötigt -> _
        path, _ = QFileDialog.getOpenFileName(self, "Datei öffnen", "", FILE_FILTER_OPEN)

        # Leerer Pfad = Benutzer hat abgebrochen
        if not path:
            return

        # try/except verhindert einen Absturz, falls die Datei nicht lesbar ist
        try:
            content = file_service.read_file(path)
        except OSError as error:
            self.show_error("Die Datei konnte nicht geöffnet werden.", error)
            return

        # HTML inklusive Formatierung laden, andere Dateien als reinen Text
        if file_service.is_html(path):
            self.editor.setHtml(content)
        else:
            self.editor.setPlainText(content)

        self.set_current_file(path)

    def save_file(self):
        """Speichert in die aktuelle Datei oder ruft 'Speichern unter' auf.

        Gibt True zurück, wenn gespeichert wurde, sonst False.
        """
        if self.current_file is None:
            return self.save_file_as()
        return self.write_to_file(self.current_file)

    def save_file_as(self):
        """Fragt nach einem Speicherort und speichert das Dokument dort.

        Gibt True zurück, wenn gespeichert wurde, sonst False (z. B. bei Abbrechen).
        """
        default_name = "Unbenannt" + file_service.DEFAULT_EXTENSION
        path, _ = QFileDialog.getSaveFileName(self, "Speichern unter", default_name, FILE_FILTER_SAVE)
        if not path:
            return False

        # Ohne Dateiendung wird die Standardendung (.html) angehängt
        return self.write_to_file(file_service.ensure_extension(path))

    def write_to_file(self, path):
        """Holt den Inhalt aus dem Textfeld und lässt ihn von file_service speichern.

        Gibt True zurück, wenn das Speichern geklappt hat, sonst False.
        """
        # .html speichert mit Formatierung, .txt nur den reinen Text
        if file_service.is_html(path):
            content = self.editor.toHtml()
        else:
            content = self.editor.toPlainText()

        try:
            file_service.write_file(path, content)
        except OSError as error:
            self.show_error("Die Datei konnte nicht gespeichert werden.", error)
            return False

        self.set_current_file(path)
        # Hinweis in der Statusleiste, verschwindet nach 3 Sekunden
        self.statusBar().showMessage("Gespeichert", 3000)
        return True

    # ── Ungespeicherte Änderungen ────────────────────────
    def maybe_save(self):
        """Fragt nach, ob ungespeicherte Änderungen gespeichert werden sollen.

        Gibt True zurück, wenn weitergemacht werden darf (gespeichert oder
        verworfen), und False, wenn der Benutzer abbricht.
        """
        # Keine Änderungen -> nichts zu fragen
        if not self.editor.document().isModified():
            return True

        box = QMessageBox(self)
        box.setWindowTitle("Ungespeicherte Änderungen")
        box.setText("Das Dokument wurde geändert.\nMöchtest du die Änderungen speichern?")
        box.setIcon(QMessageBox.Icon.Warning)
        # Eigene Buttons mit deutschem Text (Standard-Buttons wären englisch)
        save_button = box.addButton("Speichern", QMessageBox.ButtonRole.AcceptRole)
        discard_button = box.addButton("Nicht speichern", QMessageBox.ButtonRole.DestructiveRole)
        box.addButton("Abbrechen", QMessageBox.ButtonRole.RejectRole)
        box.setDefaultButton(save_button)
        box.exec()  # Dialog anzeigen und warten, bis ein Button geklickt wurde

        clicked = box.clickedButton()
        if clicked == save_button:
            # Nur weitermachen, wenn das Speichern auch wirklich geklappt hat
            return self.save_file()
        if clicked == discard_button:
            return True
        return False  # Abbrechen oder Fenster mit X geschlossen

    def closeEvent(self, event):
        """Wird von Qt automatisch aufgerufen, wenn das Fenster geschlossen wird.

        Überschreibt die Methode von QMainWindow, damit vorher nachgefragt wird.
        """
        if self.maybe_save():
            event.accept()  # Fenster darf schließen
        else:
            event.ignore()  # Schließen abbrechen

    # ── Hilfsmethoden ────────────────────────────────────
    def set_default_font(self):
        """Setzt die Standard-Schriftgröße des Textfelds."""
        font = self.editor.font()
        font.setPointSize(DEFAULT_FONT_SIZE)
        self.editor.setFont(font)

    def load_placeholders(self):
        """Lädt die Platzhaltertexte aus der Datei.

        Falls die Datei fehlt oder leer ist, gibt es einen neutralen Standardtext.
        """
        try:
            placeholders = file_service.read_lines(PLACEHOLDERS_PATH)
        except OSError:
            placeholders = []
        return placeholders or [DEFAULT_PLACEHOLDER]

    def set_random_placeholder(self):
        """Zeigt einen zufälligen Platzhaltertext im leeren Textfeld an."""
        self.editor.setPlaceholderText(random.choice(self.placeholders))

    def set_current_file(self, path):
        """Merkt sich die aktuelle Datei und markiert das Dokument als gespeichert."""
        self.current_file = path
        self.editor.document().setModified(False)
        # Zusätzlich direkt setzen: Nach clear() oder setHtml() meldet Qt
        # die Änderung nicht immer zuverlässig über das Signal.
        self.setWindowModified(False)
        self.update_title()

    def update_title(self):
        """Zeigt den Namen der aktuellen Datei in der Titelleiste an."""
        if self.current_file:
            # Path(...).name macht aus "C:/.../brief.html" nur "brief.html"
            name = Path(self.current_file).name
        else:
            name = "Unbenannt"
        # [*] ist ein Platzhalter von Qt: Dort erscheint ein *, solange
        # es ungespeicherte Änderungen gibt (siehe setWindowModified).
        self.setWindowTitle(f"{name}[*] - Tippsi")

    def show_error(self, message, error):
        """Zeigt eine Fehlermeldung als Popup an."""
        QMessageBox.warning(self, "Fehler", f"{message}\n\n{error}")


# ── Programmstart ────────────────────────────────────────
# Wird nur ausgeführt, wenn die Datei direkt gestartet wird (python main.py)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Einheitlichen Qt-Stil setzen, bevor Fenster erstellt werden
    app.setStyle(QT_STYLE)
    window = TippsiWindow()
    window.show()
    sys.exit(app.exec())