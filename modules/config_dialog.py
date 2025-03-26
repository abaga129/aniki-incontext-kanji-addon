# config_dialog.py

from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo

def get_all_decks():
    return list(mw.col.decks.all_names())

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Select Deck")
        self.layout = QVBoxLayout(self)

        self.comboVocab = QComboBox(self)
        self.comboVocab.addItems(get_all_decks())        
        self.comboVocab.currentTextChanged.connect(self.on_vocab_deck_changed)

        self.comboVocabField = QComboBox(self)
        self.comboVocabField.setEnabled(False)

        self.comboKanji = QComboBox(self)
        self.comboKanji.addItems(get_all_decks())
        self.comboKanji.currentTextChanged.connect(self.on_kanji_deck_changed)

        self.comboKanjiField = QComboBox(self)
        self.comboKanjiField.setEnabled(False)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout.addWidget(QLabel("Choose Vocab deck:"))
        self.layout.addWidget(self.comboVocab)

        self.layout.addWidget(QLabel("Choose Vocab term field:"))
        self.layout.addWidget(self.comboVocabField)

        self.layout.addWidget(QLabel("Choose Kanji deck:"))
        self.layout.addWidget(self.comboKanji)

        self.layout.addWidget(QLabel("Choose Kanji term field:"))
        self.layout.addWidget(self.comboKanjiField)

        self.layout.addWidget(self.button_box)

        # Load previously saved config
        config = mw.addonManager.getConfig(__name__)
        if config.get("selected_vocab_deck") in get_all_decks():
            deck_name = config["selected_vocab_deck"]
            self.comboVocab.setCurrentText(deck_name)
            field_names = self.get_field_names_from_did(mw.col.decks.id(deck_name), self.comboVocabField)
            # self.on_vocab_deck_changed(deck_name)
            # print(config["selected_vocab_field"])
            # print(field_names)
            if field_names and config.get("selected_vocab_field") in field_names:
            #     print("Setting combobox on")
                self.comboVocabField.clear()
                self.comboVocabField.addItems(field_names)
                self.comboVocabField.setCurrentText(config["selected_vocab_field"])
                self.comboVocabField.setEnabled(True)
        if config.get("selected_kanji_deck") in get_all_decks():
            deck_name = config["selected_kanji_deck"]
            self.comboKanji.setCurrentText(deck_name)
            field_names = self.get_field_names_from_did(mw.col.decks.id(deck_name), self.comboKanjiField)
            if field_names:
                self.comboKanjiField.clear()
                self.comboKanjiField.addItems(field_names)
                self.comboKanjiField.setEnabled(True)
                if config.get("selected_kanji_field") in field_names:
                    self.comboKanjiField.setCurrentText(config["selected_kanji_field"])

    def accept(self):
        selected_vocab_deck = self.comboVocab.currentText()
        selected_kanji_deck = self.comboKanji.currentText()
        selected_vocab_field = self.comboVocabField.currentText()
        selected_kanji_field = self.comboKanjiField.currentText()
        config = mw.addonManager.getConfig(__name__)
        config["selected_vocab_deck"] = selected_vocab_deck
        config["selected_kanji_deck"] = selected_kanji_deck
        config["selected_vocab_field"] = selected_vocab_field
        config["selected_kanji_field"] = selected_kanji_field
        mw.addonManager.writeConfig(__name__, config)
        # showInfo(f"Saved deck: {selected_deck}\n")
        super().accept()

    def get_field_names_from_did(self, did: str, combo: QComboBox):
        cids = mw.col.db.list("SELECT id FROM cards WHERE did = ? LIMIT 1", did)
        if not cids:
            combo.clear()
            combo.setEnabled(False)
            return

        nid = mw.col.db.scalar("SELECT nid FROM cards WHERE id = ?", cids[0])
        if not nid:
            combo.clear()
            combo.setEnabled(False)
            return

        note = mw.col.get_note(nid)
        model = note.note_type()
        field_names = [f["name"] for f in model["flds"]]
        if field_names is None:
            return ["None"]
        else:
            return field_names


    def on_vocab_deck_changed(self, deck_name: str):
        try:
            print(f"on_vocab_deck_changed {deck_name}")
            # Try to get the note type used in this deck
            did = mw.col.decks.id(deck_name)
            print(did)
            field_names = self.get_field_names_from_did(did, self.comboVocabField)
            print(field_names)

            if field_names:
                self.comboVocabField.clear()
                self.comboVocabField.addItems(field_names)
                self.comboVocabField.setEnabled(True)
        except Exception as e:
            print(f"Error populate fields for deck {deck_name}: {e}")

    def on_kanji_deck_changed(self, deck_name: str):
        try:
            # Try to get the note type used in this deck
            did = mw.col.decks.id(deck_name)
            field_names = self.get_field_names_from_did(did, self.comboKanjiField)

            if field_names:
                self.comboKanjiField.clear()
                self.comboKanjiField.addItems(field_names)
                self.comboKanjiField.setEnabled(True)
        except Exception as e:
            print(f"Error populate fields for deck {deck_name}: {e}")

def open_config_dialog():
    dialog = ConfigDialog(mw)
    dialog.exec()
