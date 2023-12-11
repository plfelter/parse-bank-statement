from dataclasses import dataclass, field
from pathlib import Path
import fitz
import re
import locale
import contextlib
from datetime import datetime
import numpy as np
import pandas as pd


@dataclass(kw_only=True)
class Statement:
    pdf: Path

    pages: list[str] = field(init=False)
    emission_date: datetime = field(init=False)
    headers: list[str] = field(init=False)
    accounts: pd.DataFrame = field(init=False)
    transactions: pd.DataFrame = field(init=False)

    def __post_init__(self):
        self.pages = self.get_pages_content()
        if not self.is_statement():
            raise Exception(
                f"The file {self.pdf} is not a 'La Banque Postale' statement (or is not properly formatted)."
            )
        self.emission_date = self.get_emission_date()
        self.headers = self.get_transactions_headers()
        self.accounts = self.get_accounts_start_pos()
        self.transactions = self.get_all_transactions()
        self.match_transactions_with_accounts()

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

    def get_accounts_start_pos(self) -> pd.DataFrame:
        matches = list(
            re.finditer(
                r"\n(?P<account_name>[a-zA-Z ]+) n°(?P<account_id>[\w ]+)\n",
                "".join(self.pages),
                flags=re.DOTALL,
            )
        )
        return pd.DataFrame(
            {
                "start": [m.start() for m in matches],
                "account_name": [m.group("account_name") for m in matches],
                "account_id": [m.group("account_id") for m in matches],
            }
        ).set_index("start")

    def get_all_transactions(self) -> pd.DataFrame:
        matches = list(
            re.finditer(
                r"(?P<date>\d\d/\d\d)[\s\n](?P<name>.*?)\n(?P<amount>[\d ]+,\d{2})",
                "".join(self.pages),
                flags=re.DOTALL,
            )
        )
        statements = pd.DataFrame(
            {
                "start": [m.start() for m in matches],
                "date": [m.group("date") for m in matches],
                "name": [m.group("name") for m in matches],
                "amount": [m.group("amount") for m in matches],
            }
        ).set_index("start")

        statements.loc[:, "amount"] = statements.loc[:, "amount"].apply(
            lambda s: float(s.replace(",", ".").replace(" ", ""))
        )
        return statements

    def match_transactions_with_accounts(self):
        account_match_table = pd.DataFrame(
            {i: self.transactions.index - i for i in self.accounts.index},
            index=self.transactions.index,
        ).astype(float)
        account_match_table.values[account_match_table.values < 0] = np.nan
        self.transactions["account_start_in_doc"] = account_match_table.idxmin(axis=1)
        self.transactions = self.transactions.join(
            self.accounts, on="account_start_in_doc"
        )
        self.transactions.drop(["account_start_in_doc"], axis=1, inplace=True)


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
