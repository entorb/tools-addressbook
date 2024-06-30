"""Unit Tests."""
# ruff: noqa: D103 DTZ011 PLR2004 S101

import datetime as dt

from bday_mail_sender_today import calc_age, calc_fields, get_next_bday

DATE_TODAY = dt.date.today()


def test_calc_age() -> None:
    assert calc_age(bday=DATE_TODAY, today=DATE_TODAY) == 0
    assert calc_age(bday=dt.date(1900, 2, 2), today=dt.date(2000, 2, 2)) == 100
    assert calc_age(bday=dt.date(1900, 2, 2), today=dt.date(2000, 2, 3)) == 100
    assert calc_age(bday=dt.date(1900, 2, 2), today=dt.date(2000, 12, 31)) == 100
    assert calc_age(bday=dt.date(1900, 2, 2), today=dt.date(2000, 2, 1)) == 99


test_calc_age()


def test_get_next_bday() -> None:
    assert get_next_bday(
        bday=dt.date(1900, 2, 2), today=dt.date(2000, 2, 2)
    ) == dt.date(2000, 2, 2)
    assert get_next_bday(
        bday=dt.date(1900, 2, 2), today=dt.date(2000, 2, 1)
    ) == dt.date(2000, 2, 2)
    assert get_next_bday(
        bday=dt.date(1900, 2, 2), today=dt.date(2000, 2, 3)
    ) == dt.date(2001, 2, 2)


test_get_next_bday()


def test_calc_fields() -> None:
    card = {
        "n": "Firstname Lastname",
        "bday": "19000202",
    }
    card2 = {
        "n": "Firstname Lastname",
        "bday": "1900-02-02",
        "days_next_bday": 0,
        "age": 100,
    }
    assert calc_fields(card, today=dt.date(2000, 2, 2)) == card2


test_calc_fields()
