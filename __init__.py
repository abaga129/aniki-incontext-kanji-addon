from aqt import QMenu, mw
from aqt.qt import QAction
from .config_dialog import open_config_dialog
from .hooks import on_vocab_card_learned
import sys
import os

if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

menu = QMenu("In-context Kanji", mw)
action = QAction("Configure", mw)
action.triggered.connect(open_config_dialog)
menu.addAction(action)
mw.form.menuTools.addMenu(menu)
