"""
Tippsi – eine süße Textverarbeitung
Uni-Projekt, erstellt mit Python und PySide6 (Qt)

Diese Datei startet die App und baut das Hauptfenster.
"""

# ── Imports ──────────────────────────────────────────────
# sys = Standard-Python-Modul, damit können wir mit dem System reden
# (z. B. Startargumente lesen und das Programm sauber beenden)
import sys

# Aus PySide6 holen wir uns drei Bausteine:
# - QApplication: die App selbst (davon gibt es immer genau eine)
# - QMainWindow:  ein fertiges Hauptfenster mit Platz für Menü, Toolbar usw.
# - QTextEdit:    ein Textfeld, das Formatierung (fett, kursiv …) schon kann
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit


# ── Das Hauptfenster ─────────────────────────────────────
class TippsiWindow(QMainWindow):
    """Das Hauptfenster von Tippsi.

    Erbt von QMainWindow, d. h. es kann alles, was ein normales
    Qt-Fenster kann, und wir ergänzen nur unsere eigenen Sachen.
    """

    def __init__(self):
        """Konstruktor: läuft automatisch, sobald das Fenster erstellt wird."""

        # Zuerst das normale Qt-Fenster einrichten lassen
        # (sonst fehlen Rahmen, Menüleiste usw.)
        super().__init__()

        # --- Fenster-Grundeinstellungen ---
        self.setWindowTitle("Tippsi 🎀")   # Text oben in der Titelleiste
        self.resize(900, 650)              # Startgröße: Breite x Höhe in Pixeln

        # --- Das Textfeld ---
        # "self." bedeutet: Das Textfeld gehört zu diesem Fenster.
        # So können wir später von überall darauf zugreifen (z. B. beim Speichern).
        self.editor = QTextEdit()

        # Grauer Hinweistext, solange das Feld leer ist
        self.editor.setPlaceholderText("Schreib hier los... ✨")

        # Textfeld in die Mitte des Fensters setzen
        # (das "Central Widget" ist der Hauptbereich eines QMainWindow)
        self.setCentralWidget(self.editor)

        # --- Menüleiste ---
        # menuBar() gibt uns die Leiste oben im Fenster.
        # Die Menüs sind noch leer – Funktionen bauen wir später ein.
        menu = self.menuBar()
        menu.addMenu("Datei")        # später: Neu, Öffnen, Speichern
        menu.addMenu("Bearbeiten")   # später: Rückgängig, Suchen …
        menu.addMenu("Format")       # später: Fett, Kursiv, Schriftgröße …

        # --- Der süße Look 💕 ---
        # QSS (Qt Style Sheets) funktioniert fast wie CSS bei Webseiten:
        # Man sagt, welches Element welche Farbe, Rand, Schrift usw. bekommt.
        self.setStyleSheet("""
            /* Hintergrund des ganzen Fensters: zartes Rosa */
            QMainWindow { background-color: #FFE4EC; }

            /* Menüleiste oben: kräftigeres Rosa, weiße fette Schrift */
            QMenuBar {
                background-color: #FFB6C8;
                color: white;
                font-weight: bold;
            }

            /* Menüpunkt, über dem gerade die Maus ist: noch etwas dunkler */
            QMenuBar::item:selected { background-color: #FF8FAB; }

            /* Das Textfeld: fast weiß, rosa Rand, runde Ecken */
            QTextEdit {
                background-color: #FFFAFC;
                color: #4A4A4A;              /* Textfarbe: dunkelgrau */
                border: 2px solid #FFB6C8;   /* Rand: 2 Pixel, rosa */
                border-radius: 12px;         /* runde Ecken */
                margin: 16px;                /* Abstand nach außen */
                padding: 12px;               /* Abstand nach innen */
                font-size: 14px;
            }
        """)


# ── Programmstart ────────────────────────────────────────
# Dieser Block läuft nur, wenn man die Datei direkt startet
# (python main.py) – nicht, wenn sie von einer anderen Datei importiert wird.
if __name__ == "__main__":
    # 1. Die App erstellen (sys.argv = Startargumente, braucht Qt intern)
    app = QApplication(sys.argv)

    # 2. Unser Fenster erstellen und anzeigen
    window = TippsiWindow()
    window.show()

    # 3. Die App laufen lassen: app.exec() wartet jetzt auf Klicks und
    #    Tastendrücke, bis das Fenster geschlossen wird.
    #    sys.exit() beendet danach das Programm sauber.
    sys.exit(app.exec())