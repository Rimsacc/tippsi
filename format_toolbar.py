"""
Formatierungs-Toolbar von Tippsi: fett, kursiv, unterstrichen,
Schriftart und Schriftgröße.

Die Toolbar arbeitet mit einem QTextEdit zusammen:
- Klickt man einen Button, wird die Formatierung im Textfeld geändert.
- Bewegt man den Cursor im Text, zeigt die Toolbar die Formatierung
  an dieser Stelle an (z. B. ist "F" gedrückt, wenn der Text fett ist).
"""

from PySide6.QtGui import QAction, QFont, QKeySequence
from PySide6.QtWidgets import QComboBox, QFontComboBox, QToolBar

# Schriftgrößen, die in der Auswahlliste angeboten werden (in Punkt)
FONT_SIZES = [8, 9, 10, 11, 12, 14, 16, 18, 20, 24, 28, 36, 48, 72]


class FormatToolbar(QToolBar):
    """Toolbar mit den wichtigsten Formatierungsfunktionen."""

    def __init__(self, editor, parent=None):
        """Erstellt die Toolbar für das übergebene Textfeld (QTextEdit)."""
        super().__init__("Formatierung", parent)
        self.editor = editor

        # Toolbar soll nicht verschoben werden können
        self.setMovable(False)

        self._create_font_widgets()
        self.addSeparator()
        self._create_style_actions()

        # Observer: Immer wenn sich die Formatierung an der Cursorposition
        # ändert, aktualisiert sich die Toolbar automatisch.
        self.editor.currentCharFormatChanged.connect(self.update_from_editor)
        self.update_from_editor()

    # ── Aufbau ───────────────────────────────────────────
    def _create_font_widgets(self):
        """Erstellt die Auswahllisten für Schriftart und Schriftgröße."""
        # QFontComboBox zeigt automatisch alle installierten Schriftarten an
        self.font_box = QFontComboBox()
        self.font_box.setToolTip("Schriftart")
        self.font_box.currentFontChanged.connect(self.set_font_family)
        self.addWidget(self.font_box)

        self.size_box = QComboBox()
        self.size_box.setToolTip("Schriftgröße")
        self.size_box.setEditable(True)  # eigene Größen eintippen erlaubt
        self.size_box.addItems([str(size) for size in FONT_SIZES])
        self.size_box.textActivated.connect(self.set_font_size)
        self.addWidget(self.size_box)

    def _create_style_actions(self):
        """Erstellt die Buttons für fett, kursiv und unterstrichen."""
        self.bold_action = self._make_style_action(
            "F", "Fett", QKeySequence.StandardKey.Bold, self.set_bold
        )
        self.italic_action = self._make_style_action(
            "K", "Kursiv", QKeySequence.StandardKey.Italic, self.editor.setFontItalic
        )
        self.underline_action = self._make_style_action(
            "U", "Unterstrichen", QKeySequence.StandardKey.Underline, self.editor.setFontUnderline
        )

        # Buttons selbst passend darstellen: F fett, K kursiv, U unterstrichen
        self._style_button_text(self.bold_action, bold=True)
        self._style_button_text(self.italic_action, italic=True)
        self._style_button_text(self.underline_action, underline=True)

    def _make_style_action(self, text, name, shortcut, slot):
        """Hilfsmethode: erstellt einen An/Aus-Button mit Tastenkürzel."""
        action = QAction(text, self)
        action.setCheckable(True)  # Button bleibt gedrückt, solange aktiv
        action.setShortcut(shortcut)
        # Tooltip mit Tastenkürzel, z. B. "Fett (Strg+B)".
        # NativeText zeigt das Kürzel in der Sprache des Systems an.
        shortcut_text = action.shortcut().toString(QKeySequence.SequenceFormat.NativeText)
        action.setToolTip(f"{name} ({shortcut_text})")
        # toggled liefert True/False mit, je nachdem ob der Button gedrückt ist
        action.toggled.connect(slot)
        self.addAction(action)
        return action

    def _style_button_text(self, action, bold=False, italic=False, underline=False):
        """Setzt die Schrift des Button-Texts (z. B. ein fettes F)."""
        font = QFont()
        font.setBold(bold)
        font.setItalic(italic)
        font.setUnderline(underline)
        action.setFont(font)

    # ── Formatierung anwenden ────────────────────────────
    def set_bold(self, checked):
        """Schaltet fett an oder aus."""
        weight = QFont.Weight.Bold if checked else QFont.Weight.Normal
        self.editor.setFontWeight(weight)

    def set_font_family(self, font):
        """Setzt die Schriftart für den markierten Text bzw. ab dem Cursor."""
        self.editor.setFontFamily(font.family())
        self.editor.setFocus()  # zurück ins Textfeld, damit man weitertippen kann

    def set_font_size(self, text):
        """Setzt die Schriftgröße. Ungültige Eingaben (z. B. Buchstaben) werden ignoriert."""
        try:
            size = float(text.replace(",", "."))
        except ValueError:
            return
        if size > 0:
            self.editor.setFontPointSize(size)
            self.editor.setFocus()

    # ── Anzeige aktualisieren ────────────────────────────
    def update_from_editor(self):
        """Zeigt die Formatierung an der aktuellen Cursorposition in der Toolbar an."""
        font = self.editor.currentFont()

        # Signale kurz blockieren: Sonst würde das Setzen der Buttons
        # die Formatierung im Text gleich nochmal ändern.
        widgets = [self.bold_action, self.italic_action, self.underline_action,
                   self.font_box, self.size_box]
        for widget in widgets:
            widget.blockSignals(True)

        self.bold_action.setChecked(font.bold())
        self.italic_action.setChecked(font.italic())
        self.underline_action.setChecked(font.underline())
        self.font_box.setCurrentFont(font)
        self.size_box.setCurrentText(f"{font.pointSizeF():g}")

        for widget in widgets:
            widget.blockSignals(False)