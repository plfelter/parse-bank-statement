from pathlib import Path
import pandas as pd
import fitz
import re
import time
import locale
import contextlib
from datetime import datetime


@contextlib.contextmanager
def setlocale(*args, **kw):
    saved = locale.setlocale(locale.LC_ALL)
    yield locale.setlocale(*args, **kw)
    locale.setlocale(locale.LC_ALL, saved)


def get_emission_date(statement: Path) -> None | datetime:
    with fitz.open(statement) as doc:
        first_page: str = doc[0].get_text()
        if not re.findall(r"Relevé de vo.* - n°.*", first_page):
            return None
        else:
            with setlocale(locale.LC_TIME, "fr_FR.UTF-8"):
                date_str: str = re.search(
                    r"Relevé édité le (?P<date>\d+ \w+ \d{4})", first_page
                ).group("date")
                datet: datetime = datetime.strptime(date_str, "%d %B %Y")
            # Probleme: le relevé change de nom: de CCP à compte en avril/mai 2017
            # statement_nb: int = int(
            #     re.search("Relevé de vos comptes - n° (?P<num>\d+)", first_page).group(
            #         "num"
            #     )
            # )
            # if statement_nb != datet.month:
            #     raise Exception(
            #         f"File: {statement}\nLe numéro de relevé devrait être égal au numéro du mois du relevé"
            #     )
            return date_str, datet
