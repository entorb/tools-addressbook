#!/usr/bin/env python3
"""
Export a filtered bday-only addressbook.

fields: BDAY FN N
"""

import re
from pathlib import Path

import vobject  # pip install vobject

file_in = Path("addressbook.vcf")
file_out = Path("bday_only.vcf")

with file_in.open(encoding="utf-8") as f:
    obj = vobject.readComponents(f.read())  # type: ignore
contacts: list[vobject.base.Component] = list(obj)

contacts_filtered: list[vobject.base.Component] = []

for card in contacts:
    # card.prettyPrint()
    # s = card.serialize()
    # d = card.contents

    if "bday" not in card.contents:
        continue

    # remove all fields but "bday", "n"
    card.contents = {
        key: value for key, value in card.contents.items() if key in ("n", "bday")
    }

    # bday: remove parameters from bday field: 'VALUE': ['DATE']
    card.contents["bday"][0].params = {}  # type: ignore
    # remove "-"
    card.contents["bday"][0].value = card.contents["bday"][0].value.replace("-", "")  # type: ignore
    # apple uses year 1604 for unset years, I use 1900
    if card.contents["bday"][0].value.startswith("1604"):  # type: ignore
        card.contents["bday"][0].value = "1900" + card.contents["bday"][0].value[4:]  # type: ignore

    # recreate fn based on n
    card.add("fn")
    n = card.contents["n"][0]
    fn = f"{n.value.given} {n.value.additional} {n.value.family}"  # type: ignore
    fn = re.sub(r"\s+", " ", fn)
    card.fn.value = fn

    contacts_filtered.append(card)

# sort by fn
contacts_filtered = sorted(contacts_filtered, key=lambda x: x.fn.value)

with file_out.open(mode="w", encoding="utf-8", newline="\n") as fh:
    for card in contacts_filtered:
        fh.write(card.serialize())
