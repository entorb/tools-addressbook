#!/usr/bin/env python3
"""
Convert vcf to sorted list of cleaned cards.

converts vcf to a list, sorted by Full Name (FN) field,
to allow for comparison of 2 backups of the same address book
"""

import codecs
from pathlib import Path

import vobject  # pip install vobject

file_in = Path("contacts.vcf")

file_out = file_in.with_suffix(".sorted-cleared.vcf")

with codecs.open(str(file_in), encoding="utf-8") as f:
    obj = vobject.readComponents(f.read())  # type: ignore
# contacts = [contact for contact in obj]
contacts = list(obj)
d_all_cards_by_name = {}

l_tags_to_remove = ["rev", "uid", "adr", "prodid", "photo"]

for card in contacts:
    # card.prettyPrint()
    # remove field REV, PHOTO, ADR
    if "rev" in card.contents:
        del card.contents["rev"]
    if "uid" in card.contents:
        del card.contents["uid"]
    if "photo" in card.contents:
        del card.contents["photo"]
    if "adr" in card.contents:
        del card.contents["adr"]
    s = card.serialize()
    d = card.contents
    fn = d["fn"][0].value

    # TODO: assert fn not in d_all_cards_by_name, f"ERROR: {fn} is not unique"

    d_all_cards_by_name[fn] = s

l_names = sorted(d_all_cards_by_name.keys())

with file_out.open(mode="w", encoding="utf-8", newline="\n") as fh_out:
    for name in l_names:
        card = d_all_cards_by_name[name]
        fh_out.write(card)
