# -*- coding: utf-8 -*-
from typing import Literal
from aqt.gui_hooks import reviewer_did_answer_card, Card
from aqt import mw
from aqt.reviewer import Reviewer

@reviewer_did_answer_card.append
def on_vocab_card_learned(reviewer: Reviewer, card: Card, ease: Literal[1, 2, 3, 4]):
    config = mw.addonManager.getConfig(__name__)
    selected_deck = config.get("selected_vocab_deck")
    vocab_field_name = config.get("selected_vocab_field")
    kanji_deck_name = config.get("selected_kanji_deck")
    kanji_field_name = config.get("selected_kanji_field")

    # print("Config")
    # print(selected_deck)
    # print(vocab_field_name)
    # print(kanji_deck_name)
    # print(kanji_field_name)

    if not selected_deck:
        return

    deck_name = mw.col.decks.name(card.did)
    kanji_deck = mw.col.decks.by_name(kanji_deck_name)

    if deck_name != selected_deck and kanji_deck:
        return

    if card.due:
        note = card.note()

        card_field_index = get_field_index(vocab_field_name, note)
        card_field_value = note.fields[card_field_index]

        print(len(card_field_value))

        if len(card_field_value) > 0:
            deck_id = kanji_deck["id"]
            kanji_card_id_list = mw.col.db.list(f"SELECT id FROM cards WHERE did = {deck_id}")
            kanji_cards = [mw.col.get_card(cid) for cid in kanji_card_id_list]

            for char in card_field_value:
                if is_kanji(char):
                    for kanji_card in kanji_cards:
                        kanji_note = kanji_card.note()
                        kanji_field_index = get_field_index(kanji_field_name, kanji_note)
                        kanji_field_value = kanji_note.fields[kanji_field_index]
                        if kanji_field_value == char:
                            print(f"Found Match! {kanji_field_value}")
                            print(kanji_field_value)
                            bump_new_card_to_top(kanji_card)

def get_field_index (field_name: str, note):
    # Get the model (aka note type)
    model = note.note_type()
    field_names = [fld['name'] for fld in model['flds']]

    # Find the index of the field
    if field_name in field_names:
        index = field_names.index(field_name)
        return index
    else:
        print(f"Field '{field_name}' not found in note type.")
        return 0

def bump_new_card_to_top(card):
    if card.type != 0:
        print("Card is not new.")
        return

    # Get the minimum due for new cards in the same deck
    deck_id = card.did
    cids = mw.col.db.list(
        "SELECT id FROM cards WHERE did = ? AND type = 0 ORDER BY due ASC LIMIT 1", deck_id
    )

    if cids:
        top_card_id = cids[0]
        top_due = mw.col.db.scalar("SELECT due FROM cards WHERE id = ?", top_card_id)
        card.due = top_due - 1  # move this card before the current top
    else:
        card.due = 0  # make it the first if no others exist

    card.flush()

def is_kanji(char):
    codepoint = ord(char)
    return (
        0x4E00 <= codepoint <= 0x9FFF or  # CJK Unified Ideographs
        0x3400 <= codepoint <= 0x4DBF or  # CJK Extension A
        0x20000 <= codepoint <= 0x2A6DF or  # CJK Extension B
        0x2A700 <= codepoint <= 0x2B73F or  # CJK Extension C
        0x2B740 <= codepoint <= 0x2B81F or  # CJK Extension D
        0x2B820 <= codepoint <= 0x2CEAF or  # CJK Extension E
        0x2CEB0 <= codepoint <= 0x2EBEF     # CJK Extension F-G
    )
