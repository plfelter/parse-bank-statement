from pathlib import Path
import fitz
import re
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
                date_t: datetime = datetime.strptime(date_str, "%d %B %Y")
            return date_t


# TODO: write function to retrieve all transactions from a bank statement file
#   This function should:
#       - Try to classify each transaction between debits and credits
#         This guess could use the title wording (ACHAT, PRELEVEMENT, VIREMENT DE/POUR...)
#       - check the coherence of this classification with the bank
#         statement summary line "Total des opérations"
