#!/usr/bin/env python3.11
# because of webserver

# ruff: noqa: S101, PLR2004

"""
Send emails per each birthday in my addressbook.

reads a vcf address book file
extracts only name and birthday fields
generates a list of todays birthdays
send this list via emails to me
"""

import datetime as dt
import re
import sqlite3
from os import chdir
from pathlib import Path

from bday_mail_sender_today_config import ADDRESSBOOK, FILE_ON_SERVER, MY_EMAIL

# change to current dir, as addressbook is in same dir
chdir(Path(__file__).parent)

DATE_TODAY = dt.date.today()  # noqa: DTZ011
PATH_ON_SERVER = Path(FILE_ON_SERVER)
del FILE_ON_SERVER


def calc_age(bday: dt.date, today: dt.date = DATE_TODAY) -> int:
    """Calculate age from birthday."""
    age = today.year - bday.year
    if today.month < bday.month or (today.month == bday.month and today.day < bday.day):
        age -= 1
    return age


def get_next_bday(bday: dt.date, today: dt.date = DATE_TODAY) -> dt.date:
    """Calculate next birthday."""
    year_next_bday = today.year
    if bday.month < today.month or (bday.month == today.month and bday.day < today.day):
        year_next_bday += 1
    date_next_bday = dt.date(year_next_bday, bday.month, bday.day)
    return date_next_bday


def read_vcf(file_in: Path) -> list:
    """
    Read file line-by-line and filter out the relevant lines.

    filter on contacts with birthday
    returns list of dict: n:str, bday:str
    """
    contacts = []
    card = {}
    with file_in.open(encoding="utf-8") as f:
        for line in f:
            if line.startswith("N:"):
                n = line.strip()[2:]
                # Family Name; Given Name; Middle Names; Honorific Prefixes; Honorific Suffixes  # noqa: E501
                l = n.split(";")  # noqa: E741
                assert len(l) == 5, l
                card["n"] = f"{l[1]} {l[2]} {l[0]}".replace("  ", " ")

            elif line.startswith(("BDAY:", "BDAY;")):
                card["bday"] = line.strip()
                # remove all before ":" per regex
                card["bday"] = re.sub(r"^[^:]*:", "", card["bday"])
                card["bday"] = card["bday"].replace("-", "")
                # apple uses year 1604 for unset years, I usually use 1900
                if card["bday"].startswith("1604"):
                    card["bday"] = "1900" + card["bday"][4:]
                assert len(card["bday"]) == 8, card

            elif line.startswith("END:VCARD"):
                if "bday" in card:
                    contacts.append(card)
                card = {}
    return contacts


def db_connect(  # noqa: D103
    use_row_factory: bool = False,  # noqa: FBT001, FBT002
) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    con = sqlite3.connect(PATH_ON_SERVER)
    if use_row_factory:
        con.row_factory = sqlite3.Row
    cur = con.cursor()
    return con, cur


def db_disconnect(  # noqa: D103
    con: sqlite3.Connection, cur: sqlite3.Cursor
) -> None:
    cur.close()
    con.close()


def insert_new_email(  # noqa: PLR0913, D103
    con: sqlite3.Connection,
    cur: sqlite3.Cursor,
    send_to: str,
    subject: str,
    body: str,
    send_from: str = "no-reply@entorb.net",
    send_cc: str = "",
    send_bcc: str = "",
) -> None:
    cur.execute(
        "INSERT INTO outbox(send_to, subject, body, send_from, send_cc, send_bcc, date_created, date_sent) VALUES (?,?,?,?,?,?,CURRENT_TIMESTAMP, NULL)",  # noqa: E501
        (send_to, subject, body, send_from, send_cc, send_bcc),
    )
    con.commit()


def calc_fields(card: dict, today: dt.date = DATE_TODAY) -> dict:
    """
    Calculate next birthday, age, days to next bday.
    """
    date_bday = dt.date.fromisoformat(card["bday"])  # for Python >= 3.11
    assert date_bday.year >= 1700, date_bday
    card["bday"] = str(date_bday)
    date_next_bday = get_next_bday(bday=date_bday, today=today)
    card["days_next_bday"] = (date_next_bday - today).days
    card["age"] = calc_age(bday=date_bday, today=today)
    return card


if __name__ == "__main__":
    file_in = Path(ADDRESSBOOK)
    contacts = read_vcf(file_in)

    for i, contact in enumerate(contacts):
        contacts[i] = calc_fields(contact)

    # filter: only the contacts that have birthday today
    contacts = [x for x in contacts if x["days_next_bday"] == 0]
    # contacts = [x for x in contacts if 0 <= x["days_next_bday"] < 7]

    # sorting
    contacts = sorted(contacts, key=lambda x: x["n"])
    # contacts = sorted(contacts, key=lambda x: x["days_next_bday"])

    if PATH_ON_SERVER.is_file() and len(contacts) > 0:
        con, cur = db_connect(use_row_factory=True)
        for card in contacts:
            insert_new_email(
                con=con,
                cur=cur,
                send_to=MY_EMAIL,
                subject=f"BDay: {card['n']} ({card['age']})",
                body="",
            )
        db_disconnect(con, cur)
    else:
        for card in contacts:
            print(f"{card['n']} ({card['age']})")
