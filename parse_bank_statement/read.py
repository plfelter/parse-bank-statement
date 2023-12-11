from dataclasses import dataclass, field
from pathlib import Path
import fitz
import re
import locale
import contextlib
from datetime import datetime
import pandas as pd


@dataclass(kw_only=True)
class Statement:
    pdf: Path

    pages: list[str] = field(init=False)
    emission_date: datetime = field(init=False)
    headers: list[str] = field(init=False)

    def __post_init__(self):
        self.pages = self.get_pages_content()
        if not self.is_statement():
            raise Exception(
                f"The file {self.pdf} is not a 'La Banque Postale' statement (or is not properly formatted)."
            )
        self.emission_date = self.get_emission_date()
        self.headers = self.get_transactions_headers()

    def get_pages_content(self) -> list[str]:
        with fitz.open(self.pdf) as doc:
            return list(map(lambda p: p.get_text(), doc))

    def is_statement(self):
        return re.findall(r"Relevé de vo.* - n°.*", self.pages[0]) != []

    def get_emission_date(self) -> datetime:
        with setlocale(locale.LC_TIME, "fr_FR.UTF-8"):
            date_str: str = re.search(
                r"Relevé édité le (?P<date>\d+ \w+ \d{4})", self.pages[0]
            ).group("date")
            date_t: datetime = datetime.strptime(date_str, "%d %B %Y")
        return date_t

    def get_transactions_headers(self) -> list[str]:
        return re.findall(
            r"\n(?P<headers>Date\nOpération.*)\nAncien solde",
            self.pages[0],
            flags=re.DOTALL,
        )[0].split("\n")


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
                date_t: datetime = datetime.strptime(date_str, "%d %B %Y")
            return date_t


def get_transactions_headers(statement: Path) -> list[str]:
    with fitz.open(statement) as doc:
        first_page: str = doc[0].get_text()
    return re.findall(
        r"Vos opérations\n(?P<headers>.*)\nAncien solde", first_page, flags=re.DOTALL
    )[0].split("\n")


def get_transaction_tables(statement: Path) -> str | None:
    with fitz.open(statement) as doc:
        print("------------------- DOC START -------------------")
        for page in doc:
            print(page.get_text())
            print("-------------------")
        print("-------------------- DOC END --------------------")


def get_transactions(statement: Path) -> pd.DataFrame:
    get_transaction_tables(statement)


# TODO: write function to retrieve all transactions from a bank statement file
#   This function should:
#       - Try to classify each transaction between debits and credits
#         This guess could use the title wording (ACHAT, PRELEVEMENT, VIREMENT DE/POUR...)
#       - check the coherence of this classification with the bank
#         statement summary line "Total des opérations"
