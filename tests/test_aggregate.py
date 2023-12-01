import logging
from pathlib import Path
from parse_bank_statement.aggregate import get_data_availability


def test_get_data_availability():
    get_data_availability(
        list(
            (Path.cwd().parent / "data" / "statements" / "LaBanquePostale").glob(
                "*.pdf"
            )
        )
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_get_data_availability()
