#!/usr/bin/env python3
"""
Export a filtered bday-only addressbook.

fields: BDAY FN N
"""

# TODO: vobject could be replaced by simple string manipulation
# for better performance
# see bday_mail_sender_today.py

import codecs
import re
from pathlib import Path

import vobject  # pip install vobject

file_in = Path("addressbook.vcf")
file_out = Path("bday_only.vcf")

obj = vobject.readComponents(  # type: ignore
    codecs.open(str(file_in), encoding="utf-8").read(),
)
contacts: list[vobject.base.Component] = list(obj)  # type: ignore

contacts_filtered: list[vobject.base.Component] = []

for card in contacts:
    # card.prettyPrint()
    # s = card.serialize()
    # d = card.contents

    if "bday" not in card.contents:
        continue

    # bday: remove 'VALUE': ['DATE']
    card.contents["bday"][0].params = {}  # type: ignore
    # remove "-"
    card.contents["bday"][0].value = card.contents["bday"][0].value.replace("-", "")  # type: ignore
    # apple uses year 1604 for unset years, I usually use 2000
    if card.contents["bday"][0].value.startswith("1604"):  # type: ignore
        # print(card.contents["bday"][0].value)  # type: ignore
        card.contents["bday"][0].value = "1900" + card.contents["bday"][0].value[4:]  # type: ignore

    # remove all fields but "bday", "n"
    for key in card.contents.copy():  # loop over copy, to allow for deleting keys
        if key not in ("n", "bday"):
            del card.contents[key]

    # recreate fn based on n
    card.add("fn")
    n = card.contents["n"][0]
    fn = f"{n.value.given} {n.value.additional} {n.value.family}"  # type: ignore
    fn = re.sub(r"\s+", " ", fn)
    card.fn.value = fn  # type: ignore

    contacts_filtered.append(card)

# sort by fn
contacts_filtered = sorted(contacts_filtered, key=lambda x: x.fn.value)

with file_out.open(mode="w", encoding="utf-8", newline="\n") as fh:
    for card in contacts_filtered:
        fh.write(card.serialize())
